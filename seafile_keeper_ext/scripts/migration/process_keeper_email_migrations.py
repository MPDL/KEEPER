#!/usr/bin/env python3
"""
Minimal periodic worker for self-service KEEPER email migrations.

This script polls the `keeper_email_migration` table (in the keeper DB)
for rows with status='pending', then invokes the **existing**
`migrate_account.py` script **exactly as it is today** (no refactoring).

All migration-related operational scripts now live here:

    /opt/seafile/scripts/migration/

This includes:
- process_keeper_email_migrations.py   (this worker)
- migrate_account.py
- seafile_common.py
- etc.

(Note: the legacy bulk_migrate.py tool remains in its original location and is not delivered as part of this migration/ subdir.)

The KEEPER app servers have their own scripts at /opt/seafile/scripts/migration/
(for migrate_to_new_email.py etc.), but this worker runs on the automation/management host
and is placed under the same conventional path for operational scripts.

Design principles (Phase 0 - minimal approach):
- Do NOT touch or refactor migrate_account.py or seafile_common.py
- Treat the existing migration scripts as a black box / CLI tool
- This worker only orchestrates: poll DB → call existing CLI → record result

Recommended cron (example):
    */5 * * * * cd /opt/seafile/scripts/migration && python3 process_keeper_email_migrations.py >> /var/log/keeper-migration-worker.log 2>&1

Configuration is AUTO-IMPORTED (no .env required for normal use):
    - DB credentials : /opt/seafile/keeper-*.ini  (__DB_HOST__/__DB_PORT__/__DB_USER__/__DB_PASSWORD__),
                       falling back to Seafile conf/.env (SEAFILE_MYSQL_DB_*).
    - SMTP / email   : /opt/seafile/keeper-*.ini  (__EMAIL_*, __DEFAULT_FROM_EMAIL__).
    - Page URL       : derived from __SERVER_PROTOCOL__://__SERVER_NAME__ in the .ini.
    The keeper-db database name is always 'keeper-db'.

A worker .env (in this directory) is OPTIONAL and only needed to OVERRIDE the above:
    KEEPER_DB_HOST / KEEPER_DB_PORT / KEEPER_DB_NAME / KEEPER_DB_USER / KEEPER_DB_PASSWORD
    EMAIL_HOST / EMAIL_PORT / EMAIL_USE_TLS / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD / DEFAULT_FROM_EMAIL
    MIGRATION_PAGE_URL
    MIGRATION_SCRIPT_DIR=/opt/seafile/scripts/migration   # where migrate_account.py lives
    MIGRATION_ALWAYS_CREATE=0                              # 1 = always pass -c to migrate_account.py
    SEAFILE_DIR=/opt/seafile                               # base dir for locating keeper-*.ini / conf/.env

NOTE: migrate_account.py (invoked by this worker) inherits its settings from this
.env plus the worker's auto-imported environment. Auto-imported from keeper-*.ini:
MYSQL_HOST/USER/PASSWORD (same MySQL server as keeper-db) and SEAFILE_SERVER_URL
(this instance's URL). Privileged steps run LOCALLY when KEEPER_MIGRATE_SERVER is
empty / this host (no SSH). The only value you normally must set in .env is
SEAFILE_AUTH_TOKEN (admin API token) — otherwise the unattended worker would hang
on a credential prompt.

Usage (from the migration dir):
    python3 process_keeper_email_migrations.py
    python3 process_keeper_email_migrations.py --dry-run
    python3 process_keeper_email_migrations.py --list-pending   # manual ops helper
"""

import os
import glob
import re
import subprocess
import sys
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pymysql
from dotenv import load_dotenv, dotenv_values

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

load_dotenv()


def _read_keeper_ini_values(keys):
    """Read values from the KEEPER instance .ini at /opt/seafile/*keeper*.ini.

    That file (e.g. /opt/seafile/keeper-app07-qa.ini) holds the DB credentials
    as '__DB_HOST__ = ...' style lines. This mirrors the safe grep/sed parser
    used by deploy-migration.sh (loose match, value may have a trailing comment).
    """
    seafile_dir = os.getenv("SEAFILE_DIR", "/opt/seafile")
    files = sorted(set(
        glob.glob(os.path.join(seafile_dir, "*keeper*.ini"))
        + glob.glob(os.path.join(seafile_dir, "keeper*.ini"))
    ))
    found = {}
    for path in files:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    for key in keys:
                        if key in found:
                            continue
                        m = re.match(r"\s*" + re.escape(key) + r"\s*=\s*(.+?)\s*(?:[#;].*)?$", line)
                        if m:
                            val = m.group(1).strip().strip('"').strip("'")
                            if val:
                                found[key] = val
        except Exception:
            continue
        if all(k in found for k in keys):
            break
    return found


def _read_seafile_conf_env(keys):
    """Read values from the deployed Seafile conf/.env (SEAFILE_MYSQL_DB_* keys)."""
    seafile_dir = os.getenv("SEAFILE_DIR", "/opt/seafile")
    candidates = [
        os.getenv("SEAFILE_CONF_ENV"),
        os.path.join(seafile_dir, "conf", ".env"),
        "/opt/seafile/conf/.env",
        os.path.join(seafile_dir, "seafile-server-latest", "conf", ".env"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            try:
                vals = dotenv_values(path)
                picked = {k: vals.get(k) for k in keys if vals.get(k)}
                if picked:
                    return picked
            except Exception:
                continue
    return {}


# Auto-import DB settings so the worker does not need its own copy of the creds.
# Priority per value:
#   1. worker .env               (KEEPER_DB_*        - optional explicit override)
#   2. /opt/seafile/*keeper*.ini (__DB_HOST__ etc.   - the KEEPER instance .ini)
#   3. Seafile conf/.env         (SEAFILE_MYSQL_DB_* - the runtime Seafile config)
# The keeper-db database name is always 'keeper-db' (override with KEEPER_DB_NAME).
_KEEPER_INI = _read_keeper_ini_values([
    "__DB_HOST__", "__DB_PORT__", "__DB_USER__", "__DB_PASSWORD__",
    "__EMAIL_HOST__", "__EMAIL_PORT__", "__EMAIL_USE_TLS__",
    "__EMAIL_HOST_USER__", "__EMAIL_HOST_PASSWORD__", "__DEFAULT_FROM_EMAIL__",
    "__SERVER_NAME__", "__SERVER_PROTOCOL__",
])
_SEAFILE_ENV = _read_seafile_conf_env([
    "SEAFILE_MYSQL_DB_HOST", "SEAFILE_MYSQL_DB_PORT", "SEAFILE_MYSQL_DB_USER", "SEAFILE_MYSQL_DB_PASSWORD",
    "SEAFILE_SERVER_HOSTNAME", "SEAFILE_SERVER_PROTOCOL",
])


def _db_value(env_key, ini_key, seafile_key, default=None):
    return (os.getenv(env_key)
            or _KEEPER_INI.get(ini_key)
            or _SEAFILE_ENV.get(seafile_key)
            or default)


def _ini_value(env_key, ini_key, default=None):
    """worker .env override > KEEPER instance .ini value > default."""
    return os.getenv(env_key) or _KEEPER_INI.get(ini_key) or default


def _server_base_url():
    """Base URL of this KEEPER instance.

    Tries the KEEPER instance .ini (__SERVER_NAME__/__SERVER_PROTOCOL__) first,
    then the Seafile conf/.env (SEAFILE_SERVER_HOSTNAME/SEAFILE_SERVER_PROTOCOL).
    """
    name = _KEEPER_INI.get("__SERVER_NAME__") or _SEAFILE_ENV.get("SEAFILE_SERVER_HOSTNAME")
    proto = (_KEEPER_INI.get("__SERVER_PROTOCOL__")
             or _SEAFILE_ENV.get("SEAFILE_SERVER_PROTOCOL")
             or "https")
    return f"{proto}://{name}" if name else ""


DB_CONFIG = {
    "host": _db_value("KEEPER_DB_HOST", "__DB_HOST__", "SEAFILE_MYSQL_DB_HOST", "127.0.0.1"),
    "port": int(_db_value("KEEPER_DB_PORT", "__DB_PORT__", "SEAFILE_MYSQL_DB_PORT", "3306")),
    "user": _db_value("KEEPER_DB_USER", "__DB_USER__", "SEAFILE_MYSQL_DB_USER"),
    "password": _db_value("KEEPER_DB_PASSWORD", "__DB_PASSWORD__", "SEAFILE_MYSQL_DB_PASSWORD"),
    "database": os.getenv("KEEPER_DB_NAME", "keeper-db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def _export_if_empty(name, value):
    """Put a value into the environment for the migrate_account.py subprocess,
    unless it is already set to a non-empty value (an explicit .env always wins)."""
    if value and not os.environ.get(name):
        os.environ[name] = value


# migrate_account.py reads MYSQL_HOST / MYSQL_USER / MYSQL_PASSWORD directly. These
# are the same MySQL server credentials as the keeper-db connection, so import them
# from the KEEPER instance .ini (via DB_CONFIG) instead of duplicating them in .env.
# The worker runs migrate_account.py as a subprocess, which inherits this environment.
_export_if_empty("MYSQL_HOST", DB_CONFIG["host"])
_export_if_empty("MYSQL_USER", DB_CONFIG["user"])
_export_if_empty("MYSQL_PASSWORD", DB_CONFIG["password"])
# migrate_account.py / seafile_common.py read SEAFILE_SERVER_URL; default it to this
# instance's own URL (from the .ini) so it does not need to be set in .env.
_export_if_empty("SEAFILE_SERVER_URL", _server_base_url())

MIGRATION_SCRIPT_DIR = os.getenv(
    "MIGRATION_SCRIPT_DIR",
    "/opt/seafile/scripts/migration",   # All migration automation scripts live here
)
MIGRATE_SCRIPT = os.path.join(MIGRATION_SCRIPT_DIR, "migrate_account.py")

ALWAYS_CREATE = os.getenv("MIGRATION_ALWAYS_CREATE", "0") == "1"

# Email settings for notifications. Auto-imported from the KEEPER instance .ini
# (__EMAIL_*) when not overridden in the worker .env; sensible defaults otherwise.
EMAIL_HOST = _ini_value("EMAIL_HOST", "__EMAIL_HOST__", "localhost")
EMAIL_PORT = int(_ini_value("EMAIL_PORT", "__EMAIL_PORT__", "25"))
EMAIL_USE_TLS = _ini_value("EMAIL_USE_TLS", "__EMAIL_USE_TLS__", "False").lower() == "true"
EMAIL_HOST_USER = _ini_value("EMAIL_HOST_USER", "__EMAIL_HOST_USER__", "")
EMAIL_HOST_PASSWORD = _ini_value("EMAIL_HOST_PASSWORD", "__EMAIL_HOST_PASSWORD__", "")
DEFAULT_FROM_EMAIL = _ini_value("DEFAULT_FROM_EMAIL", "__DEFAULT_FROM_EMAIL__", "keeper@mpdl.mpg.de")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", DEFAULT_FROM_EMAIL)


# Link to the self-service data transfer page (used in notification emails).
# Defaults to this instance's own hostname (from the .ini) + /account/migrate/.
_BASE_URL = _server_base_url()
MIGRATION_PAGE_URL = os.getenv("MIGRATION_PAGE_URL") or (
    f"{_BASE_URL}/account/migrate/" if _BASE_URL else "https://keeper.mpdl.mpg.de/account/migrate/"
)

LOG_DIR = os.path.join(MIGRATION_SCRIPT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOCK_FILE = os.path.join(MIGRATION_SCRIPT_DIR, "migration_worker.lock")
_lock_fd = None

# -------------------------------------------------------------------
# Simple exclusive lock to prevent overlapping cron runs
# -------------------------------------------------------------------
def acquire_lock():
    """Acquire an exclusive non-blocking lock using fcntl (Unix).
    Exits cleanly if another instance is running.
    """
    import fcntl
    global _lock_fd
    try:
        _lock_fd = open(LOCK_FILE, "w")
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fd.write(str(os.getpid()))
        _lock_fd.flush()
        # Ensure we release on exit
        import atexit
        atexit.register(release_lock)
        log(f"Acquired exclusive lock (pid {os.getpid()})")
        return True
    except IOError:
        log("Another instance of the migration worker is already running. Exiting.")
        sys.exit(0)
    except Exception as e:
        log(f"Warning: could not acquire lock: {e}")
        return False

def release_lock():
    global _lock_fd
    if _lock_fd:
        try:
            import fcntl
            fcntl.flock(_lock_fd, fcntl.LOCK_UN)
        except Exception:
            pass
        _lock_fd.close()


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    # Also append to daily log file
    log_file = os.path.join(LOG_DIR, f"worker_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_db_connection():
    if not DB_CONFIG["host"] or not DB_CONFIG["user"]:
        raise RuntimeError(
            "KEEPER_DB_HOST and KEEPER_DB_USER must be set in .env"
        )
    return pymysql.connect(**DB_CONFIG)


def fetch_pending_migrations(conn):
    """Return list of pending moves that the target has confirmed, oldest first.

    Only confirmed requests (confirmed_at IS NOT NULL) are processed: the
    target must enter the code and complete the confirmation step before the
    background worker will act on the migration.
    """
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, source_email, target_email, migration_token, token_expires_at
            FROM keeper_email_migration
            WHERE status = 'pending' AND confirmed_at IS NOT NULL
            ORDER BY requested_at ASC
            LIMIT 50
            """
        )
        return cursor.fetchall()


def detect_and_recover_stuck_jobs(conn, max_age_hours: int = 6):
    """
    Find jobs that have been 'in_progress' for too long and mark them failed.
    This prevents a crashed worker from leaving jobs stuck forever.
    """
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, source_email, target_email
            FROM keeper_email_migration
            WHERE status = 'in_progress'
              AND (completed_at IS NULL OR completed_at < DATE_SUB(NOW(), INTERVAL %s HOUR))
            """,
            (max_age_hours,),
        )
        stuck = cursor.fetchall()

    if not stuck:
        return

    for job in stuck:
        mid = job["id"]
        error = f"Marked failed by worker: stuck in 'in_progress' for >{max_age_hours}h (possible crash)"
        log(f"Recovering stuck job #{mid}: {job['source_email']} → {job['target_email']}")
        mark_failed(conn, mid, error, "")
        send_migration_notification(mid, job["source_email"], job["target_email"],
                                    success=False, log_path="", error=error)


def mark_in_progress(conn, migration_id: int):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE keeper_email_migration
            SET status = 'in_progress'
            WHERE id = %s AND status = 'pending'
            """,
            (migration_id,),
        )
    conn.commit()


def mark_completed(conn, migration_id: int, log_path: str):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE keeper_email_migration
            SET status = 'completed',
                completed_at = NOW(),
                metadata = JSON_SET(COALESCE(metadata, '{}'), '$.worker_log', %s)
            WHERE id = %s
            """,
            (log_path, migration_id),
        )
    conn.commit()


def mark_failed(conn, migration_id: int, error: str, log_path: str):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE keeper_email_migration
            SET status = 'failed',
                completed_at = NOW(),
                error_message = %s,
                metadata = JSON_SET(COALESCE(metadata, '{}'), '$.worker_log', %s)
            WHERE id = %s
            """,
            (error[:2000], log_path, migration_id),
        )
    conn.commit()


def run_existing_migration_script(source: str, target: str) -> tuple[int, str, str]:
    """
    Invoke the existing migrate_account.py exactly as operators do today.

    Returns: (returncode, stdout+stderr combined, log_file_path)
    """
    cmd = [
        sys.executable,
        MIGRATE_SCRIPT,
        "--from", source,
        "--to", target,
    ]
    if ALWAYS_CREATE:
        cmd.append("-c")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_src = source.replace("@", "_at_").replace(".", "_")
    safe_tgt = target.replace("@", "_at_").replace(".", "_")
    log_filename = f"migration_{safe_src}_to_{safe_tgt}_{timestamp}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    log(f"Running: {' '.join(cmd)}")
    log(f"Output will be captured to: {log_path}")

    try:
        with open(log_path, "w", encoding="utf-8") as logfile:
            proc = subprocess.run(
                cmd,
                stdout=logfile,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=7200,  # 2 hours max per migration (large libraries)
            )
        returncode = proc.returncode
    except subprocess.TimeoutExpired:
        returncode = 124
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n\n[WORKER] ERROR: Migration timed out after 2 hours\n")
    except Exception as e:
        returncode = 1
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n[WORKER] ERROR launching migration: {e}\n")

    # Read last ~100 lines for quick error reporting
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            tail = "".join(lines[-100:])
    except Exception:
        tail = f"(could not read log file {log_path})"

    return returncode, tail, log_path


def send_migration_notification(migration_id: int, source: str, target: str, success: bool, log_path: str, error: str = None):
    """
    Notification hook for self-service migrations.

    Uses smtplib with settings from .env (EMAIL_HOST etc). Standard KEEPER email settings are used as defaults where applicable.
    Also prints a template to stdout for manual review or if email fails.

    The worker runs on the automation host and has access to the same .env as migrate_account.py.
    """
    status = "SUCCESS" if success else "FAILED"
    log(f"[{status}] Migration #{migration_id}: {source} → {target}")
    log(f"  Log file: {log_path}")
    if error:
        log(f"  Error: {error[:500]}")

    # Build message - very plain, no computer words at all
    if success:
        subject = "Keeper Data Transfer Completed"
    else:
        subject = "Problem with Keeper Data Transfer"
    body = f"""Your Keeper data (libraries, shares, and groups) has been transferred {"successfully" if success else "with a problem"}.

From: {source}
To: {target}

Please log in at https://keeper.mpdl.mpg.de using the target account to access your files and folders.

The source account will no longer be usable for Keeper.

To review the status of this data transfer:
{MIGRATION_PAGE_URL}

Verify on the identity banner at the top that you are authenticated with the correct account (SOURCE or TARGET). If the banner indicates the wrong account, log out and log in with the appropriate account, then return to the page.

If you encounter any issues, please contact {SUPPORT_EMAIL}.
"""
    if error:
        body += f"\n(For help, provide the source and target email addresses.)\n"

    # Print template always (for manual/audit) - plain language
    print("\n" + "="*60)
    print("KEEPER DATA MOVE (email sent + this note for ops)")
    print(f"Result: {status}")
    print(f"From: {source}")
    print(f"To: {target}")
    if error:
        print(f"Problem: {error[:300]}")
    print("Tell the user: Log in with the target account to access files. The source account is deactivated.")
    print("On the account data transfer page, verify the identity banner shows the correct SOURCE or TARGET account. Log out and log in if incorrect.")
    print(f"Data transfer page: {MIGRATION_PAGE_URL}")
    print("Support contact: keeper@mpdl.mpg.de")
    print("="*60 + "\n")

    # Send via smtplib
    try:
        msg = MIMEMultipart()
        msg['From'] = DEFAULT_FROM_EMAIL
        msg['To'] = ", ".join([source, target])
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        if EMAIL_HOST_USER:
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(DEFAULT_FROM_EMAIL, [source, target], msg.as_string())
        server.quit()
        log("Email notification sent successfully.")
    except Exception as e:
        log(f"Failed to send email notification: {e}")
        # Still have the print above for manual follow-up


def process_one_migration(conn, row: dict):
    mid = row["id"]
    src = row["source_email"]
    tgt = row["target_email"]

    log(f"=== Processing migration #{mid}: {src} → {tgt} ===")

    # Optimistic lock: only move forward if still pending
    mark_in_progress(conn, mid)

    returncode, tail, log_path = run_existing_migration_script(src, tgt)

    if returncode == 0:
        mark_completed(conn, mid, log_path)
        log(f"  ✓ Migration #{mid} completed successfully")
        send_migration_notification(mid, src, tgt, success=True, log_path=log_path)
    else:
        error_summary = f"Exit code {returncode}. Last output:\n{tail[:2000]}"
        mark_failed(conn, mid, error_summary, log_path)
        log(f"  ✗ Migration #{mid} FAILED (exit {returncode})")
        send_migration_notification(mid, src, tgt, success=False, log_path=log_path, error=error_summary)


def main():
    if "--list-pending" in sys.argv:
        # Manual ops helper: list pending moves without processing
        try:
            conn = get_db_connection()
            pending = fetch_pending_migrations(conn)
            if pending:
                print("Pending data moves:")
                for row in pending:
                    exp = row.get('token_expires_at', 'N/A')
                    if exp and hasattr(exp, 'strftime'):
                        exp = exp.strftime('%Y-%m-%d %H:%M')
                    print(f"  #{row['id']} {row['source_email']} → {row['target_email']} (code expires {exp})")
            else:
                print("No pending moves.")
            conn.close()
        except Exception as e:
            print(f"Error listing: {e}")
        return

    dry_run = "--dry-run" in sys.argv

    log("=== KEEPER Self-Service Migration Worker starting ===")
    if dry_run:
        log("*** DRY RUN MODE - no DB writes or migrations will be executed ***")

    # Prevent concurrent runs
    acquire_lock()

    if not os.path.exists(MIGRATE_SCRIPT):
        log(f"ERROR: migrate_account.py not found at {MIGRATE_SCRIPT}")
        log("Set MIGRATION_SCRIPT_DIR=/opt/seafile/scripts/migration in .env")
        log("All migration scripts (this worker + migrate_account.py + seafile_common.py) should live in /opt/seafile/scripts/migration/")
        sys.exit(1)

    try:
        conn = get_db_connection()
        log(f"Connected to keeper DB at {DB_CONFIG['host']}")
    except Exception as e:
        log(f"Failed to connect to keeper DB: {e}")
        sys.exit(1)

    try:
        # Recover any jobs left in in_progress from a previous crashed run
        detect_and_recover_stuck_jobs(conn)

        pending = fetch_pending_migrations(conn)
        if not pending:
            log("No pending moves found.")
            return

        log(f"Found {len(pending)} pending move(s)")

        for row in pending:
            if dry_run:
                log(f"[DRY-RUN] Would process: #{row['id']} {row['source_email']} → {row['target_email']}")
                continue

            try:
                process_one_migration(conn, row)
            except Exception as e:
                log(f"Unexpected error processing row {row['id']}: {e}")
                # Best effort: mark as failed
                try:
                    mark_failed(conn, row["id"], str(e), "")
                except Exception:
                    pass

    finally:
        conn.close()
        log("=== Worker run finished ===")


if __name__ == "__main__":
    main()