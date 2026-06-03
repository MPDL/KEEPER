# Proposed Changes for Self-Service Email Migration (KEEPER PR)

This directory contains the **proposed structure and starter files** for the overall change.

There are two parts:

1. **Web / application changes** (for the PR against https://github.com/MPDL/KEEPER)
   - `seafile_keeper_ext/`
   - `seahub-data/custom/templates/...`

2. **Operational / automation scripts** (deployed to servers)
   - `opt/seafile/scripts/migration/`  → installed as `/opt/seafile/scripts/migration/`

## How to use

1. Review the design document in the workspace: `docs/self-service-email-migration-design.md` (top level of this repo)
2. Web changes under `seafile_keeper_ext/` mirror the paths inside the KEEPER repository.
3. Scripts under `opt/seafile/scripts/migration/` should be deployed to `/opt/seafile/scripts/migration/` on the automation/management host.
4. When ready, the `seafile_keeper_ext/` parts become the actual PR to MPDL/KEEPER. The migration scripts are ops changes.

## Production Layout (as specified)

All migration-related operational scripts live under:

    /opt/seafile/scripts/migration/

This includes:
- `process_keeper_email_migrations.py` (the new self-service worker)
- `migrate_account.py`
- `seafile_common.py`
- Supporting files (requirements.txt, etc.)

The KEEPER application servers also use `/opt/seafile/scripts/migration/` for their Seafile migration helpers (e.g. `migrate_to_new_email.py`).

## Next Major Work (Phase 0 - Minimal)

**Phase 0 is intentionally minimal:**
- Do **not** refactor `migrate_account.py` or `seafile_common.py`
- The key deliverable is the worker at:
  `opt/seafile/scripts/migration/process_keeper_email_migrations.py`
  - Polls the new `keeper_email_migration` table
  - Calls the **existing** `migrate_account.py` via subprocess (same pattern as `bulk_migrate.py`)
  - Records result + logs back to the DB

**Recommended cron:**
    */5 * * * * cd /opt/seafile/scripts/migration && python3 process_keeper_email_migrations.py >> /var/log/keeper-migration-worker.log 2>&1

See `opt/seafile/scripts/migration/README.md` (after deployment) and the main design document (workspace top-level `docs/self-service-email-migration-design.md`) for full details.

## Schema change

The table definition has been committed **directly** to:

`seafile_keeper_ext/seafile-server-latest/seahub/keeper/keeper-db.sql`

A standalone copy for ops deployment is also provided at:

`opt/seafile/scripts/migration/create_keeper_email_migration_table.sql`

See the README inside `opt/seafile/scripts/migration/` for details on when to use which.

See the design document for the full phased plan.