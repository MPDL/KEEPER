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
- bulk_migrate.py (legacy)
- etc.

The KEEPER app servers have their own scripts at /opt/seafile/scripts/migration/
(for migrate_to_new_email.py etc.), but this worker runs on the automation/management host
and is placed under the same conventional path for operational scripts.

Design principles (Phase 0 - minimal approach):
- Do NOT touch or refactor migrate_account.py or seafile_common.py
- Treat the existing migration scripts as a black box / CLI tool
- This worker only orchestrates: poll DB → call existing CLI → record result

Recommended cron (example):
    */5 * * * * cd /opt/seafile/scripts/migration && python3 process_keeper_email_migrations.py >> /var/log/keeper-migration-worker.log 2>&1

Environment / .env variables (add these):
    KEEPER_DB_HOST=...
    KEEPER_DB_PORT=3306
    KEEPER_DB_NAME=keeper-db
    KEEPER_DB_USER=...
    KEEPER_DB_PASSWORD=...

    # Directory containing migrate_account.py etc. (this directory)
    MIGRATION_SCRIPT_DIR=/opt/seafile/scripts/migration

    MIGRATION_ALWAYS_CREATE=0                          # 1 = always pass -c to migrate_account.py

    # For full links (landing + direct /status/<id>/) in the notification emails sent to users
    MIGRATION_PAGE_URL=https://keeper.mpdl.mpg.de/account/migrate/

Usage (from the migration dir):
    python3 process_keeper_email_migrations.py
    python3 process_keeper_email_migrations.py --dry-run
    python3 process_keeper_email_migrations.py --list-pending   # manual ops helper
"""

import os
import subprocess
import sys
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pymysql
from dotenv import load_dotenv

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("KEEPER_DB_HOST"),
    "port": int(os.getenv("KEEPER_DB_PORT", 3306)),
    "user": os.getenv("KEEPER_DB_USER"),
    "password": os.getenv("KEEPER_DB_PASSWORD"),
    "database": os.getenv("KEEPER_DB_NAME", "keeper-db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

MIGRATION_SCRIPT_DIR = os.getenv(
    "MIGRATION_SCRIPT_DIR",
    "/opt/seafile/scripts/migration",   # All migration automation scripts live here
)
MIGRATE_SCRIPT = os.path.join(MIGRATION_SCRIPT_DIR, "migrate_account.py")

ALWAYS_CREATE = os.getenv("MIGRATION_ALWAYS_CREATE", "0") == "1"

# Email settings for notifications (from .env; defaults provided)
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 25))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "keeper@mpdl.mpg.de")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "keeper@mpdl.mpg.de")

# Link to the self-service migration page (for status / details in emails)
MIGRATION_PAGE_URL = os.getenv("MIGRATION_PAGE_URL", "https://keeper.mpdl.mpg.de/account/migrate/")

# How often this should be run (for documentation only)
RECOMMENDED_CRON = "*/5 * * * *   # every 5 minutes is a good starting point"

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
    """Return list of pending moves, oldest first."""
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, source_email, target_email, migration_token, token_expires_at
            FROM keeper_email_migration
            WHERE status = 'pending'
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
    # Full specific link to this move's status page (for the failure email)
    status_url = f"{MIGRATION_PAGE_URL}status/{migration_id}/"

    body = f"""Your Keeper data (libraries, shares, and groups) has been transferred {"successfully" if success else "with a problem"}.

From: {source}
To: {target}

Please log in at https://keeper.mpdl.mpg.de using the new email address to access your files and folders.

The old email address will no longer be usable for Keeper.

To review the status of this data transfer:
{MIGRATION_PAGE_URL}

Verify on the identity banner at the top that you are authenticated with the correct account (SOURCE or TARGET). If the banner indicates the wrong account, log out and log in with the appropriate email address, then return to the page.

Direct status link for this transfer: {status_url}

If you encounter any issues, please contact {SUPPORT_EMAIL}.
"""
    if error:
        body += f"\n(For help, tell them your old email and new email.)\n"

    # Print template always (for manual/audit) - plain language
    print("\n" + "="*60)
    print("KEEPER DATA MOVE (email sent + this note for ops)")
    print(f"Result: {status}")
    print(f"From: {source}")
    print(f"To: {target}")
    if error:
        print(f"Problem: {error[:300]}")
    print("Tell the user: Log in with the new email to access files. The old email is deactivated.")
    print("On the account migration page, verify the identity banner shows the correct SOURCE or TARGET account. Log out and log in if incorrect.")
    print(f"Migration page: {MIGRATION_PAGE_URL}")
    print(f"Direct status link: {status_url}")
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


# Backwards compat alias used by older code in this file
send_basic_notification = send_migration_notification


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