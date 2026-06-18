"""
Shared Seafile Admin API utilities.

=============================================================================
PLACEHOLDER / OPERATIONAL COPY
This is a copy of the original production script located in the
/opt/seafile/scripts/migration/ directory on the automation host.

DO NOT REFACTOR OR CHANGE THIS FILE for the self-service migration feature.
The new worker (process_keeper_email_migrations.py) and migrate_account.py
depend on this module exactly as before.

Original source of truth was maintained separately.
=============================================================================
"""

"""Shared Seafile Admin API utilities."""

import getpass
import os
import sys

import requests
from dotenv import load_dotenv, set_key

ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
API_TIMEOUT = 1800  # 30 minutes


def load_config():
    load_dotenv(ENV_FILE)
    server_url = os.getenv("SEAFILE_SERVER_URL", "").rstrip("/")
    token = os.getenv("SEAFILE_AUTH_TOKEN", "")
    if not server_url:
        print("Error: SEAFILE_SERVER_URL is not set in .env")
        sys.exit(1)
    return server_url, token


def save_token(token):
    set_key(ENV_FILE, "SEAFILE_AUTH_TOKEN", token)


def obtain_token(server_url):
    """Prompt for admin credentials and obtain an API token."""
    print("Authentication required.")
    username = input("Admin email: ")
    password = getpass.getpass("Admin password: ")
    resp = requests.post(
        f"{server_url}/api2/auth-token/",
        data={"username": username, "password": password},
        timeout=API_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"Authentication failed ({resp.status_code}): {resp.text}")
        sys.exit(1)
    token = resp.json()["token"]
    save_token(token)
    print("Authenticated successfully. Token saved to .env")
    return token


def auth_headers(token):
    return {"Authorization": f"Token {token}"}


def validate_token(server_url, token):
    """Return True if the token is still valid."""
    if not token:
        return False
    resp = requests.get(
        f"{server_url}/api2/auth/ping/",
        headers=auth_headers(token),
        timeout=API_TIMEOUT,
    )
    return resp.status_code == 200


def ensure_auth(server_url, token):
    """Return a valid token, prompting for credentials if needed."""
    if validate_token(server_url, token):
        return token
    return obtain_token(server_url)


def get_user(server_url, token, email):
    """Check if a user exists (works for DB, LDAP, and SSO users)."""
    resp = requests.get(
        f"{server_url}/api/v2.1/admin/search-user/",
        headers=auth_headers(token),
        params={"query": email},
        timeout=API_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"Error searching user {email} ({resp.status_code}): {resp.text}")
        sys.exit(1)
    data = resp.json()
    user_list = data.get("user_list", [])
    q = email.lower()
    # Prefer an EXACT account-id (email field) match first. This is important when
    # an old account (email-as-id) and an SSO account (uuid@auth.local) share the
    # same contact email: passing the exact id then resolves deterministically.
    for user in user_list:
        if user.get("email", "").lower() == q:
            return True, user
    # Fall back to contact_email match (SSO users searched by their address).
    for user in user_list:
        if user.get("contact_email", "").lower() == q:
            return True, user
    return False, None


def get_user_libraries(server_url, token, owner_email):
    """Return list of libraries owned by a user (handles pagination)."""
    repos = []
    page = 1
    per_page = 100
    while True:
        resp = requests.get(
            f"{server_url}/api/v2.1/admin/libraries/",
            headers=auth_headers(token),
            params={"owner": owner_email, "page": page, "per_page": per_page},
            timeout=API_TIMEOUT,
        )
        if resp.status_code != 200:
            print(f"Error listing libraries for {owner_email} ({resp.status_code}): {resp.text}")
            sys.exit(1)
        data = resp.json()
        repo_list = data.get("repos", [])
        # Normalize: API returns 'id' but we use 'repo_id' internally
        for r in repo_list:
            if "repo_id" not in r and "id" in r:
                r["repo_id"] = r["id"]
        repos.extend(repo_list)
        if not data.get("has_next_page", False):
            break
        page += 1
    return repos


def _get_shares_by_type(server_url, token, repo_id, share_type):
    """Fetch shares of a given type for a library. Returns a list."""
    resp = requests.get(
        f"{server_url}/api/v2.1/admin/shares/",
        headers=auth_headers(token),
        params={"repo_id": repo_id, "share_type": share_type},
        timeout=API_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"  Warning: could not get {share_type} shares for {repo_id} "
              f"({resp.status_code}): {resp.text}")
        return []
    data = resp.json()
    # Response may be a list or a dict with a list inside
    if isinstance(data, list):
        return data
    # Try common dict keys
    for key in (f"{share_type}_shares", "shares", "share_list", share_type):
        if key in data and isinstance(data[key], list):
            return data[key]
    return []


def get_library_shares(server_url, token, repo_id):
    """Return (user_shares, group_shares) for a library. Best-effort: warns on failure."""
    user_shares = _get_shares_by_type(server_url, token, repo_id, "user")
    group_shares = _get_shares_by_type(server_url, token, repo_id, "group")
    return user_shares, group_shares


def generate_user_token(server_url, admin_token, user_email):
    """Generate an API token for a user via admin impersonation."""
    resp = requests.post(
        f"{server_url}/api/v2.1/admin/generate-user-auth-token/",
        headers=auth_headers(admin_token),
        json={"email": user_email},
        timeout=API_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"Error generating token for {user_email} ({resp.status_code}): {resp.text}")
        return None
    return resp.json().get("token")


def get_user_shared_folders(server_url, user_token):
    """List all folders shared by a user (requires impersonated user token)."""
    resp = requests.get(
        f"{server_url}/api/v2.1/shared-folders/",
        headers=auth_headers(user_token),
        timeout=API_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"Error listing shared folders ({resp.status_code}): {resp.text}")
        return []
    data = resp.json()
    if isinstance(data, list):
        return data
    # May be wrapped in a key
    for key in ("shared_folders", "shares", "share_list"):
        if key in data and isinstance(data[key], list):
            return data[key]
    return []


def get_folder_shares(server_url, admin_token, repo_id, path):
    """Get user and group shares for a specific folder path within a library."""
    user_shares = _get_shares_by_type_with_path(server_url, admin_token, repo_id, path, "user")
    group_shares = _get_shares_by_type_with_path(server_url, admin_token, repo_id, path, "group")
    return user_shares, group_shares


def _get_shares_by_type_with_path(server_url, token, repo_id, path, share_type):
    """Fetch shares of a given type for a specific path within a library."""
    resp = requests.get(
        f"{server_url}/api/v2.1/admin/shares/",
        headers=auth_headers(token),
        params={"repo_id": repo_id, "path": path, "share_type": share_type},
        timeout=API_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"  Warning: could not get {share_type} shares for {repo_id} path={path} "
              f"({resp.status_code}): {resp.text}")
        return []
    data = resp.json()
    if isinstance(data, list):
        return data
    for key in (f"{share_type}_shares", "shares", "share_list", share_type):
        if key in data and isinstance(data[key], list):
            return data[key]
    return []


def restore_folder_shares(server_url, token, repo_id, path, user_shares, group_shares, skip_user=None):
    """Re-apply user and group shares to a specific folder path within a library."""
    errors = 0
    for share in user_shares:
        username = share.get("username", share.get("user_email", share.get("share_to", "")))
        permission = share.get("permission", "r")
        if skip_user and username.lower() == skip_user.lower():
            continue
        resp = requests.post(
            f"{server_url}/api/v2.1/admin/shares/",
            headers=auth_headers(token),
            data={
                "repo_id": repo_id,
                "path": path,
                "share_type": "user",
                "share_to": username,
                "permission": permission,
            },
            timeout=API_TIMEOUT,
        )
        if resp.status_code not in (200, 201):
            print(f"    Warning: failed to restore user share {username} on {repo_id} path={path} "
                  f"({resp.status_code}): {resp.text}")
            errors += 1

    for share in group_shares:
        group_id = share.get("group_id", share.get("share_to", ""))
        permission = share.get("permission", "r")
        resp = requests.post(
            f"{server_url}/api/v2.1/admin/shares/",
            headers=auth_headers(token),
            data={
                "repo_id": repo_id,
                "path": path,
                "share_type": "group",
                "share_to": str(group_id),
                "permission": permission,
            },
            timeout=API_TIMEOUT,
        )
        if resp.status_code not in (200, 201):
            print(f"    Warning: failed to restore group share {group_id} on {repo_id} path={path} "
                  f"({resp.status_code}): {resp.text}")
            errors += 1

    return errors


def get_user_groups(server_url, user_token):
    """List all groups the user belongs to (requires impersonated user token)."""
    resp = requests.get(
        f"{server_url}/api2/groups/",
        headers=auth_headers(user_token),
        timeout=API_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"Error listing groups ({resp.status_code}): {resp.text}")
        return []
    data = resp.json()
    if isinstance(data, list):
        return data
    return data.get("groups", [])


def get_group_members(server_url, admin_token, group_id):
    """List members of a group via admin API. Returns list of member dicts."""
    resp = requests.get(
        f"{server_url}/api/v2.1/admin/groups/{group_id}/members/",
        headers=auth_headers(admin_token),
        timeout=API_TIMEOUT,
    )
    if resp.status_code != 200:
        print(f"  Warning: could not get members for group {group_id} "
              f"({resp.status_code}): {resp.text}")
        return []
    data = resp.json()
    if isinstance(data, list):
        return data
    return data.get("members", [])


def is_group_admin(server_url, admin_token, group_id, user_email):
    """Check if a user is an admin of a group. Returns True/False."""
    members = get_group_members(server_url, admin_token, group_id)
    for m in members:
        if m.get("email", "").lower() == user_email.lower():
            return bool(m.get("is_admin", False))
    return False


def set_group_member_admin(server_url, admin_token, group_id, user_email):
    """Set a group member as admin via admin API. Returns True on success."""
    resp = requests.put(
        f"{server_url}/api/v2.1/admin/groups/{group_id}/members/{user_email}/",
        headers=auth_headers(admin_token),
        data={"is_admin": "true"},
        timeout=API_TIMEOUT,
    )
    if resp.status_code == 200:
        return True
    print(f"  Warning: failed to set {user_email} as admin in group {group_id} "
          f"({resp.status_code}): {resp.text}")
    return False


def restore_library_shares(server_url, token, repo_id, user_shares, group_shares, skip_user=None):
    """Re-apply user and group shares to a library.
    skip_user: skip any user share where username matches (case-insensitive)."""
    errors = 0
    for share in user_shares:
        username = share.get("username", share.get("user_email", share.get("share_to", "")))
        permission = share.get("permission", "r")
        if skip_user and username.lower() == skip_user.lower():
            continue
        # Use form-encoded data — Django endpoint calls request.data.getlist()
        resp = requests.post(
            f"{server_url}/api/v2.1/admin/shares/",
            headers=auth_headers(token),
            data={
                "repo_id": repo_id,
                "share_type": "user",
                "share_to": username,
                "permission": permission,
            },
            timeout=API_TIMEOUT,
        )
        if resp.status_code not in (200, 201):
            print(f"    Warning: failed to restore user share {username} on {repo_id} "
                  f"({resp.status_code}): {resp.text}")
            errors += 1

    for share in group_shares:
        group_id = share.get("group_id", share.get("share_to", ""))
        permission = share.get("permission", "r")
        resp = requests.post(
            f"{server_url}/api/v2.1/admin/shares/",
            headers=auth_headers(token),
            data={
                "repo_id": repo_id,
                "share_type": "group",
                "share_to": str(group_id),
                "permission": permission,
            },
            timeout=API_TIMEOUT,
        )
        if resp.status_code not in (200, 201):
            print(f"    Warning: failed to restore group share {group_id} on {repo_id} "
                  f"({resp.status_code}): {resp.text}")
            errors += 1

    return errors
