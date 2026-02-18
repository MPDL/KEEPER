#!/usr/bin/env python
"""
Migrate Keeper-related objects from old_email / old_user to new_email / new_user.
Also renames storage directories where applicable.

Usage:
    python migrate_keeper_user.py old@example.com new@example.com [--apply]

    Without --apply → dry run (shows what would be done)
    With --apply    → actually saves DB changes + renames directories
"""

import sys
import os
import shutil
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
import django
django.setup()

from django.db import transaction
from django.db.models import Q
from django.conf import settings

from seahub.profile.models import Profile
from keeper.models import Catalog, CDC, DoiRepo, BCertificate, KeeperArchiveOwnerQuota, KeeperArchive


# Usually something like: /srv/keeper/bloxberg-certs or /media/keeper/bcert
# BLOXBERG_CERTS_STORAGE = getattr(settings, 'BLOXBERG_CERTS_STORAGE', '/path/to/__BLOXBERG_CERTS_STORAGE__')
BLOXBERG_CERTS_STORAGE = getattr(settings, 'BLOXBERG_CERTS_STORAGE', None)

# Usually something like: /keeper/hpss or /mnt/hpss/archive or similar
HPSS_USER = getattr(settings, 'HPSS_USER', None)
HPSS_URL = getattr(settings, 'HPSS_URL', None)
HPSS_STORAGE_PATH = getattr(settings, 'HPSS_STORAGE_PATH', None)

# ────────────────────────────────────────────────

DRY_RUN = "--apply" not in sys.argv

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

old_email = sys.argv[1].strip()
new_email  = sys.argv[2].strip()

if DRY_RUN:
    print("╔════════════════════════════════════════════╗")
    print("║                DRY RUN MODE                ║")
    print("║   No changes will be written to disk/DB    ║")
    print("╚════════════════════════════════════════════╝\n")

def rename_directory(old_path: Path, new_path: Path, what: str) -> bool:
    """Rename directory if it exists. Returns True if renamed (or would be)."""
    if not old_path.exists():
        print(f"→ {what} directory does NOT exist: {old_path}")
        return False

    if new_path.exists():
        print(f"⚠  Target {what} directory already exists: {new_path}")
        print("   → Skipping rename to avoid data loss")
        return False

    print(f"→ Renaming {what} directory:")
    print(f"     {old_path}  →")
    print(f"     {new_path}")

    if DRY_RUN:
        return True

    try:
        shutil.move(str(old_path), str(new_path))
        print("   → Success")
        return True
    except Exception as e:
        print(f"   → FAILED: {e}")
        return False


@transaction.atomic
def keeper_migrate_user():
    # ─── 1. Resolve old and new internal user ────────────────────────────────
    try:
        old_profile = Profile.objects.get(Q(contact_email=old_email) | Q(user=old_email))
        old_id = old_profile.user
        print(f"Old user:  {old_id: <36} ({old_email})")
    except Profile.DoesNotExist:
        print(f"✗ User/profile not found for: {old_email}")
        sys.exit(1)

    try:
        new_profile = Profile.objects.get(Q(contact_email=new_email) | Q(user=new_email))
        new_id = new_profile.user
        print(f"New user:  {new_id: <36} ({new_email})")
    except Profile.DoesNotExist:
        print(f"✗ Target user not found: {new_email}")
        sys.exit(1)

    if old_id == new_id:
        print("Old and new user are the same → nothing to migrate.")
        sys.exit(0)


    # ─── 2. Helper to update owner field ─────────────────────────────────────
    def update_owner(model, field="owner", extra_filter=None):
        qs = model.objects.filter(**{field: old_id})
        if extra_filter:
            qs = qs.filter(extra_filter)
        count = qs.count()
        if count == 0:
            print(f"→ {model.__name__}: 0 records")
            return 0
        print(f"→ {model.__name__}: {count} record{'s' if count != 1 else ''}")
        if DRY_RUN:
            return count
        qs.update(**{field: new_id})
        return count

    # ─── 3. Update all owner fields ──────────────────────────────────────────
    total_updated = 0

    total_updated += update_owner(Catalog)
    total_updated += update_owner(CDC)
    total_updated += update_owner(DoiRepo)
    total_updated += update_owner(BCertificate)
    total_updated += update_owner(KeeperArchiveOwnerQuota)
    total_updated += update_owner(KeeperArchive)

    print(f"\nTotal database records updated: {total_updated}")

    # ─── 4. Rename certificate storage directory ─────────────────────────────
    if BLOXBERG_CERTS_STORAGE and Path(BLOXBERG_CERTS_STORAGE).is_dir():
        old_cert_dir = Path(BLOXBERG_CERTS_STORAGE) / old_id
        new_cert_dir = Path(BLOXBERG_CERTS_STORAGE) / new_id
        rename_directory(old_cert_dir, new_cert_dir, "Bloxberg certificates")

    # ─── 5. Rename HPSS / archive storage directory ──────────────────────────
    if HPSS_USER and HPSS_URL and HPSS_STORAGE_PATH:
        old_archive_dir = Path(HPSS_STORAGE_PATH) / old_id
        new_archive_dir = Path(HPSS_STORAGE_PATH) / new_id
        print(f"""→ Migrate archive directory on remote HPSS server manually:
$ssh {HPSS_USER}@{HPSS_URL}
$mv {old_archive_dir} {new_archive_dir}""")
        
    
    # ─── 6. Final notes ──────────────────────────────────────────────────────
    print("\n" + "═"*60)
    if DRY_RUN:
        print("Dry run completed. Review output ↑")
        print("Run with --apply to apply changes.")
    else:
        print("Migration completed.")
        print("→ Recommended post-migration checks:")
        print("  • Test login with both old & new email")
        print("  • Verify certificates are still downloadable")
        print("  • Check Keeper archives are accessible")
        print("  • If using SSO/LDAP/social auth:")
        print("    → Consider updating social_django UserSocialAuth.uid")
        print("      UPDATE social_auth_usersocialauth SET uid = %s WHERE uid = %s;", new_id, old_id)

    # Optional: also migrate social auth (uncomment if needed)
    # from social_django.models import UserSocialAuth
    # cnt = UserSocialAuth.objects.filter(uid=old_id).update(uid=new_id)
    # print(f"→ Updated {cnt} social auth mapping(s)")


if __name__ == "__main__":
    keeper_migrate_user()



