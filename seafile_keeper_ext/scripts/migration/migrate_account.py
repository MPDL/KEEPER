#!/usr/bin/env python3
"""
Migrate a Seafile account (repos, groups, shares) from one user to another.

=============================================================================
PLACEHOLDER / OPERATIONAL COPY
This is a copy of the original production script located in the
/opt/seafile/scripts/migration/ directory on the automation host.

The new worker (process_keeper_email_migrations.py) calls this script via
subprocess, exactly like bulk_migrate.py did before.

LOCAL EXECUTION: when KEEPER_MIGRATE_SERVER is empty or refers to this host
(local/localhost/this hostname), the privileged MySQL / keeper-script steps run
locally via subprocess instead of over SSH (no SSH agent / KEEPER_SSH_USER needed).

Original source of truth was maintained separately.
Any changes to migration logic should be done carefully and tested.
=============================================================================
"""

"""Migrate a Seafile account (repos, groups, shares) from one user to another."""

import argparse
import json
import os
import secrets
import socket
import string
import subprocess
import sys
from datetime import datetime

import paramiko
import requests
from seafile_common import (
    load_config, ensure_auth, auth_headers, get_user,
    get_user_libraries, get_library_shares, restore_library_shares,
    generate_user_token, get_user_shared_folders, get_folder_shares,
    restore_folder_shares, get_user_groups, is_group_admin,
    set_group_member_admin,
    API_TIMEOUT,
)


def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%&*+-="
    pwd = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%&*+-="),
    ]
    pwd += [secrets.choice(alphabet) for _ in range(length - 4)]
    pwd_list = list(pwd)
    secrets.SystemRandom().shuffle(pwd_list)
    return "".join(pwd_list)


def create_user(server_url, token, email):
    """Create a new user with a placeholder password (will be overwritten with the old account's password)."""
    password = "YOUR CURRENT PASSWORD"
    resp = requests.post(
        f"{server_url}/api/v2.1/admin/users/",
        headers=auth_headers(token),
        json={"email": email, "password": password},
        timeout=API_TIMEOUT,
    )
    if resp.status_code in (200, 201):
        print(f"  Created user: {email}")
        return True
    print(f"Error creating user {email} ({resp.status_code}): {resp.text}")
    return None


def migrate_account(server_url, token, from_api_email, to_api_email):
    """Migrate all data (repos, groups, shares) from one user to another. Returns True on success."""
    resp = requests.post(
        f"{server_url}/api2/accounts/{from_api_email}/",
        headers=auth_headers(token),
        data={"op": "migrate", "to_user": to_api_email},
        timeout=API_TIMEOUT,
    )
    if resp.status_code == 200:
        print("Migration completed successfully.")
        return True
    print(f"Migration failed ({resp.status_code}): {resp.text}")
    return False


def verify_user(server_url, token, label, email, allow_create):
    """Verify a user exists; optionally create if missing.
    Returns (api_email, was_created) or (None, False)."""
    exists, info = get_user(server_url, token, email)
    if exists:
        api_email = info.get("email", email)
        print(f"[{label}] User {email} exists (API id: {api_email}).")
        return api_email, False

    print(f"[{label}] User {email} does NOT exist.")
    if allow_create:
        if create_user(server_url, token, email) is None:
            return None, False
        # Look up the newly created user to get the actual API email
        exists, info = get_user(server_url, token, email)
        if exists:
            api_email = info.get("email", email)
            print(f"  [{label}] Created user API id: {api_email}")
            return api_email, True
        return email, True
    return None, False


def capture_sharing_permissions(server_url, token, from_api_email,
                                from_user=None, to_user=None,
                                to_api_email=None, to_created=False):
    """Capture all sharing permissions for libraries owned by from_api_email."""
    print("\nCapturing sharing permissions...")
    libraries = get_user_libraries(server_url, token, from_api_email)
    print(f"  Found {len(libraries)} libraries.")

    shares_data = {
        "captured_at": datetime.now().isoformat(),
        "from_user": from_user or from_api_email,
        "from_api_email": from_api_email,
        "to_user": to_user or "",
        "to_api_email": to_api_email or "",
        "to_user_created": to_created,
        "owner": from_api_email,
        "libraries": [],
    }

    # Capture library-level shares
    for lib in libraries:
        repo_id = lib["repo_id"]
        repo_name = lib.get("name", repo_id)
        user_shares, group_shares = get_library_shares(server_url, token, repo_id)

        if user_shares or group_shares:
            shares_data["libraries"].append({
                "repo_id": repo_id,
                "repo_name": repo_name,
                "user_shares": user_shares,
                "group_shares": group_shares,
                "folder_shares": [],
            })
            print(f"  {repo_name}: {len(user_shares)} user share(s), "
                  f"{len(group_shares)} group share(s)")

    # Capture folder-level shares via user impersonation
    print("\nCapturing folder-level shares...")
    user_token = generate_user_token(server_url, token, from_api_email)
    if not user_token:
        print("  Warning: could not generate user token, skipping folder-level shares.")
    else:
        shared_folders = get_user_shared_folders(server_url, user_token)
        print(f"  Found {len(shared_folders)} shared folder(s).")

        # Group shared folders by repo_id
        folders_by_repo = {}
        for sf in shared_folders:
            repo_id = sf.get("repo_id", sf.get("origin_repo_id", ""))
            path = sf.get("path", sf.get("folder_path", ""))
            if repo_id and path:
                folders_by_repo.setdefault(repo_id, set()).add(path)

        for repo_id, paths in folders_by_repo.items():
            # Find or create library entry in shares_data
            lib_entry = None
            for entry in shares_data["libraries"]:
                if entry["repo_id"] == repo_id:
                    lib_entry = entry
                    break
            if not lib_entry:
                # Look up library name
                repo_name = repo_id
                for lib in libraries:
                    if lib["repo_id"] == repo_id:
                        repo_name = lib.get("name", repo_id)
                        break
                lib_entry = {
                    "repo_id": repo_id,
                    "repo_name": repo_name,
                    "user_shares": [],
                    "group_shares": [],
                    "folder_shares": [],
                }
                shares_data["libraries"].append(lib_entry)

            for path in sorted(paths):
                f_user_shares, f_group_shares = get_folder_shares(server_url, token, repo_id, path)
                if f_user_shares or f_group_shares:
                    lib_entry["folder_shares"].append({
                        "path": path,
                        "user_shares": f_user_shares,
                        "group_shares": f_group_shares,
                    })
                    print(f"  {lib_entry['repo_name']} [{path}]: "
                          f"{len(f_user_shares)} user, {len(f_group_shares)} group")

    total_folder_shares = sum(
        len(lib.get("folder_shares", [])) for lib in shares_data["libraries"]
    )
    print(f"  Total libraries with shares: {len(shares_data['libraries'])}")
    print(f"  Total folder-level shares: {total_folder_shares}")

    # Capture group admin roles
    print("\nCapturing group admin roles...")
    admin_groups = []
    if not user_token:
        user_token = generate_user_token(server_url, token, from_api_email)
    if not user_token:
        print("  Warning: could not generate user token, skipping group admin capture.")
    else:
        groups = get_user_groups(server_url, user_token)
        print(f"  User belongs to {len(groups)} group(s).")
        for grp in groups:
            group_id = grp.get("id")
            group_name = grp.get("name", str(group_id))
            if group_id and is_group_admin(server_url, token, group_id, from_api_email):
                admin_groups.append({"group_id": group_id, "group_name": group_name})
                print(f"  Admin in: {group_name} (id={group_id})")
        if not admin_groups:
            print("  User is not admin in any group.")
    shares_data["group_admin_roles"] = admin_groups

    return shares_data


def save_shares_to_file(shares_data, from_user, to_user):
    """Save shares data to a JSON file alongside this script. Returns the file path."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_from = from_user.replace("@", "_at_").replace(".", "_")
    safe_to = to_user.replace("@", "_at_").replace(".", "_")
    filename = f"shares_backup_{safe_from}_to_{safe_to}_{timestamp}.json"
    filepath = os.path.join(script_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(shares_data, f, indent=2, ensure_ascii=False)

    print(f"  Shares saved to: {filepath}")
    return filepath


def restore_sharing_permissions(server_url, token, shares_data, from_api_email):
    """Restore sharing permissions from captured data. Returns True if all OK."""
    libraries = shares_data.get("libraries", [])
    if not libraries:
        print("\nNo sharing permissions to restore.")
        return True

    print(f"\nRestoring sharing permissions for {len(libraries)} libraries...")
    total_errors = 0
    for lib in libraries:
        repo_id = lib["repo_id"]
        repo_name = lib.get("repo_name", repo_id)
        print(f"  Restoring shares for: {repo_name}")

        # Restore library-level shares
        errors = restore_library_shares(
            server_url, token, repo_id,
            lib.get("user_shares", []),
            lib.get("group_shares", []),
            skip_user=from_api_email,
        )
        total_errors += errors

        # Restore folder-level shares
        for folder in lib.get("folder_shares", []):
            path = folder["path"]
            print(f"    Restoring folder shares for: {repo_name} [{path}]")
            errors = restore_folder_shares(
                server_url, token, repo_id, path,
                folder.get("user_shares", []),
                folder.get("group_shares", []),
                skip_user=from_api_email,
            )
            total_errors += errors

    if total_errors:
        print(f"\nError: {total_errors} share(s) failed to restore. "
              "Check output above and use the JSON backup to retry manually.")
        return False

    print("\nAll sharing permissions restored successfully.")
    return True


def restore_group_admin_roles(server_url, token, shares_data, to_api_email):
    """Restore group admin roles for the migrated user. Returns True if all OK."""
    admin_groups = shares_data.get("group_admin_roles", [])
    if not admin_groups:
        return True

    print(f"\nRestoring group admin roles for {len(admin_groups)} group(s)...")
    errors = 0
    for grp in admin_groups:
        group_id = grp["group_id"]
        group_name = grp.get("group_name", str(group_id))
        if set_group_member_admin(server_url, token, group_id, to_api_email):
            print(f"  Restored admin role in: {group_name} (id={group_id})")
        else:
            errors += 1

    if errors:
        print(f"\nWarning: {errors} group admin role(s) failed to restore.")
        return False

    print("All group admin roles restored successfully.")
    return True


def run_keeper_migration(migrate_server, ssh_user, from_api_email, to_api_email):
    """Run migrate_to_new_email.py on the Keeper app server via SSH using paramiko."""
    cmd = (
        f"/opt/seafile/scripts/run_keeper_script.sh "
        f"/opt/seafile/scripts/migration/migrate_to_new_email.py "
        f"{from_api_email} {to_api_email} --apply"
    )
    print(f"\nRunning Keeper migration on {migrate_server or 'local'}...")
    print(f"  Command: {cmd}")

    exit_code, out, err = _ssh_run(migrate_server, ssh_user, cmd)
    if exit_code is None:
        return False
    if out:
        print(f"  stdout:\n{out}")
    if err:
        print(f"  stderr:\n{err}")
    if exit_code != 0:
        print(f"Keeper migration failed (exit code {exit_code}).")
        return False
    print("Keeper migration completed successfully.")
    return True


def copy_user_password(migrate_server, ssh_user, from_api_email, to_api_email,
                       mysql_user, mysql_password, mysql_host):
    """Copy the password from the old account to the new account and clear force-password-change flag."""
    mysql_auth = f"mysql -u {mysql_user} -p'{mysql_password}' -h {mysql_host}"
    cmd = (
        f'{mysql_auth} ccnet-db -e "'
        f"SET @pw=(SELECT passwd FROM EmailUser WHERE email='{from_api_email}'); "
        f"UPDATE EmailUser SET passwd=@pw WHERE email='{to_api_email}';"
        f'" && '
        f'{mysql_auth} seahub-db -e "'
        f"UPDATE options_useroptions SET option_val='0' "
        f"WHERE email='{to_api_email}' AND option_key='force_passwd_change';"
        f'"'
    )
    print(f"\nCopying password from {from_api_email} to {to_api_email}...")

    exit_code, out, err = _ssh_run(migrate_server, ssh_user, cmd)
    if exit_code is None:
        return False
    if out:
        print(f"  stdout:\n{out}")
    if err:
        print(f"  stderr:\n{err}")
    if exit_code != 0:
        print(f"Password copy failed (exit code {exit_code}).")
        return False
    print("Password copied successfully.")
    return True


def _is_local(migrate_server):
    """True when the migration target is this same host, so commands can run
    locally instead of over SSH. Empty/local/localhost/this hostname all count."""
    if not migrate_server:
        return True
    s = migrate_server.strip().lower()
    if s in ("local", "localhost", "127.0.0.1", "::1"):
        return True
    try:
        if s in (socket.gethostname().lower(), socket.getfqdn().lower()):
            return True
    except Exception:
        pass
    return False


def _ssh_run(migrate_server, ssh_user, cmd):
    """Run a command and return (exit_code, stdout, stderr), or (None, None, None)
    on failure (after printing the reason).

    Runs LOCALLY via subprocess when migrate_server refers to this host
    (see _is_local); otherwise runs remotely over paramiko/SSH.
    """
    if _is_local(migrate_server):
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()
        except Exception as e:
            print(f"Error running local command: {e}")
            return None, None, None

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(migrate_server, username=ssh_user, allow_agent=True)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode().strip(), stderr.read().decode().strip()
    except paramiko.AuthenticationException:
        print("Error: SSH authentication failed. Is the SSH agent forwarded?")
        return None, None, None
    except paramiko.SSHException as e:
        print(f"Error: SSH connection failed: {e}")
        return None, None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None
    finally:
        ssh.close()


def capture_admin_share_permissions(migrate_server, ssh_user, from_api_email, from_user,
                                    mysql_user, mysql_password, mysql_host):
    """Snapshot share_extrasharepermission rows where share_to matches the source user.

    Matches on BOTH the current api id (from_api_email — could be …@auth.local for
    SSO-converted users) AND the operator-supplied --from argument (the pre-SSO
    @mpdl.mpg.de address), since orphans can be pinned to either. Returns a list of
    {id, repo_id, share_to, permission} dicts (or None on failure) for callers to
    attach to shares_data so they land in the shared JSON backup."""
    select_cmd = (
        f"mysql -u {mysql_user} -p'{mysql_password}' -h {mysql_host} seahub-db "
        f"--batch --skip-column-names -e "
        f"\"SELECT id, repo_id, share_to, permission FROM share_extrasharepermission "
        f"WHERE share_to IN ('{from_api_email}','{from_user}');\""
    )
    print(f"\nCapturing inbound admin share permissions for {from_api_email} / {from_user}...")
    exit_code, out, err = _ssh_run(migrate_server, ssh_user, select_cmd)
    if exit_code is None:
        return None
    if err:
        print(f"  stderr:\n{err}")
    if exit_code != 0:
        print(f"Admin share permission capture failed (exit code {exit_code}).")
        return None

    rows = []
    if out:
        for line in out.splitlines():
            fields = line.split("\t")
            if len(fields) >= 4:
                rows.append({
                    "id": int(fields[0]),
                    "repo_id": fields[1],
                    "share_to": fields[2],
                    "permission": fields[3],
                })
    print(f"  {len(rows)} admin share row(s) captured.")
    return rows


def migrate_admin_share_permissions(migrate_server, ssh_user, from_api_email, from_user,
                                    to_api_email,
                                    mysql_user, mysql_password, mysql_host):
    """Re-point admin-level share permissions from source to target user.

    The Seafile migrate API updates SharedRepo.to_email but does NOT touch
    seahub-db.share_extrasharepermission, which holds the 'admin' elevation
    on libraries shared TO the migrated user. Without this step those rows
    stay pinned to the old email and the user silently loses admin on
    incoming shares. Matches share_to against BOTH the current api id and
    the original --from argument so pre-SSO and post-SSO orphans are caught.
    The LEFT JOIN guard makes the INSERT idempotent."""
    cmd = (
        f"mysql -u {mysql_user} -p'{mysql_password}' -h {mysql_host} seahub-db -e "
        f"\"INSERT INTO share_extrasharepermission (repo_id, share_to, permission) "
        f"SELECT a.repo_id, '{to_api_email}', a.permission "
        f"FROM share_extrasharepermission a "
        f"LEFT JOIN share_extrasharepermission b "
        f"ON b.repo_id=a.repo_id AND b.share_to='{to_api_email}' "
        f"WHERE a.share_to IN ('{from_api_email}','{from_user}') AND b.id IS NULL;\""
    )
    print(f"\nMigrating admin-level share permissions from {from_api_email} / {from_user} to {to_api_email}...")
    exit_code, out, err = _ssh_run(migrate_server, ssh_user, cmd)
    if exit_code is None:
        return False
    if out:
        print(f"  stdout:\n{out}")
    if err:
        print(f"  stderr:\n{err}")
    if exit_code != 0:
        print(f"Admin share permission migration failed (exit code {exit_code}).")
        return False
    print("Admin share permissions migrated successfully.")
    return True


def delete_sessions(migrate_server, ssh_user, from_api_email,
                    mysql_user, mysql_password, mysql_host):
    """Delete old session tokens for the source account via MySQL."""
    cmd = (
        f'mysql -u {mysql_user} -p\'{mysql_password}\' -h {mysql_host} seahub-db -e '
        f'"DELETE FROM api2_tokenv2 WHERE user=\'{from_api_email}\';"'
    )
    print(f"\nDeleting old sessions for {from_api_email} on {migrate_server or 'local'}...")

    exit_code, out, err = _ssh_run(migrate_server, ssh_user, cmd)
    if exit_code is None:
        return False
    if out:
        print(f"  stdout:\n{out}")
    if err:
        print(f"  stderr:\n{err}")
    if exit_code != 0:
        print(f"Session deletion failed (exit code {exit_code}).")
        return False
    print("Old sessions deleted successfully.")
    return True


def deactivate_user(server_url, token, api_email):
    """Set a user account to is_active=false."""
    resp = requests.put(
        f"{server_url}/api/v2.1/admin/users/{api_email}/",
        headers=auth_headers(token),
        json={"is_active": False},
        timeout=API_TIMEOUT,
    )
    if resp.status_code == 200:
        print(f"\nUser {api_email} deactivated successfully.")
        return True
    print(f"\nFailed to deactivate {api_email} ({resp.status_code}): {resp.text}")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Migrate a Seafile account to another user."
    )
    parser.add_argument(
        "--from", "-f", dest="from_user", required=True,
        help="Source user email address",
    )
    parser.add_argument(
        "--to", "-t", dest="to_user", required=True,
        help="Target user email address",
    )
    parser.add_argument(
        "-c", "--create", action="store_true",
        help="Create missing users with a random password",
    )
    parser.add_argument(
        "--skip-shares", action="store_true",
        help="Skip capturing and restoring sharing permissions",
    )
    args = parser.parse_args()

    server_url, token = load_config()
    token = ensure_auth(server_url, token)

    migrate_server = os.getenv("KEEPER_MIGRATE_SERVER", "")
    ssh_user = os.getenv("KEEPER_SSH_USER", "")
    mysql_user = os.getenv("MYSQL_USER", "")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_host = os.getenv("MYSQL_HOST", "")
    # KEEPER_MIGRATE_SERVER / KEEPER_SSH_USER are optional: when empty (or the value
    # refers to this host) the privileged steps run locally via subprocess, no SSH.
    if migrate_server and not _is_local(migrate_server) and not ssh_user:
        print("Error: KEEPER_SSH_USER is not set in .env (required for remote SSH execution).")
        sys.exit(1)
    if not mysql_user:
        print("Error: MYSQL_USER is not set in .env.")
        sys.exit(1)
    if not mysql_password:
        print("Error: MYSQL_PASSWORD is not set in .env.")
        sys.exit(1)
    if not mysql_host:
        print("Error: MYSQL_HOST is not set in .env.")
        sys.exit(1)

    from_api_email, _ = verify_user(server_url, token, "FROM", args.from_user, args.create)
    to_api_email, to_created = verify_user(server_url, token, "TO", args.to_user, args.create)

    if not from_api_email or not to_api_email:
        print("\nOne or more users do not exist. Use -c to create them.")
        sys.exit(1)

    # Copy password to newly created account immediately
    if to_created:
        if not copy_user_password(migrate_server, ssh_user, from_api_email, to_api_email,
                                     mysql_user, mysql_password, mysql_host):
            sys.exit(1)

    # Step 1: Capture sharing permissions before migration
    shares_data = None
    if not args.skip_shares:
        shares_data = capture_sharing_permissions(
            server_url, token, from_api_email,
            from_user=args.from_user, to_user=args.to_user,
            to_api_email=to_api_email, to_created=to_created,
        )
        admin_rows = capture_admin_share_permissions(
            migrate_server, ssh_user, from_api_email, args.from_user,
            mysql_user, mysql_password, mysql_host,
        )
        shares_data["inbound_admin_shares"] = admin_rows if admin_rows is not None else []
        save_shares_to_file(shares_data, args.from_user, args.to_user)

    # Step 2: Perform migration
    print(f"\nMigrating account: {args.from_user} -> {args.to_user}")
    if not migrate_account(server_url, token, from_api_email, to_api_email):
        sys.exit(1)

    # Step 3: Restore sharing permissions after migration
    if shares_data and not args.skip_shares:
        if not restore_sharing_permissions(server_url, token, shares_data, from_api_email):
            print("\nAborting: share restoration had errors. Fix them before continuing.")
            sys.exit(1)

    # Step 3b: Restore group admin roles
    if shares_data and not args.skip_shares:
        restore_group_admin_roles(server_url, token, shares_data, to_api_email)

    # Step 3c: Migrate inbound admin-level share permissions (libraries shared TO source)
    if not migrate_admin_share_permissions(migrate_server, ssh_user,
                                           from_api_email, args.from_user, to_api_email,
                                           mysql_user, mysql_password, mysql_host):
        sys.exit(1)

    # Step 4: Run Keeper migration script on app server
    if not run_keeper_migration(migrate_server, ssh_user, from_api_email, to_api_email):
        sys.exit(1)

    # Step 5: Delete old session tokens
    if not delete_sessions(migrate_server, ssh_user, from_api_email,
                           mysql_user, mysql_password, mysql_host):
        sys.exit(1)

    # Step 6: Deactivate the old account
    if not deactivate_user(server_url, token, from_api_email):
        sys.exit(1)


if __name__ == "__main__":
    main()
