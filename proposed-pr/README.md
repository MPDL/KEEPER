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

## Deployment (new dedicated support)

For deploying *only* the migration feature on top of an already-deployed KEEPER:

- From `seafile_keeper_ext/`:
  - `./deploy-migration.sh standalone`   (prompting, safe overlay)
  - `./keeper_setup.sh deploy-migration`
- Via build.py (integrated/"slipstream"):
  - `python build.py deploy --migration`
- The single parameter to `deploy-migration.sh` selects the mode (slipstream vs standalone) and is wired from build.py + keeper_setup.sh.

Full redeploys (`deploy-all`, `build.py deploy --all`, etc.) continue to work and will pick up the migration/ subdirectories automatically.

**Web UI URL registration (included in this PR)**

The PR now includes the change to the core `seahub/seahub/urls.py` (see `proposed-pr/seahub/seahub/urls.py` for the exact proposed content with the addition in the KEEPER custom block).

The direct include `re_path(r'^account/migrate/', include('keeper.migration.urls'))` is added so the self-service migration page is at `/account/migrate/` (with the required prominent SOURCE vs TARGET identity banners).

The `keeper/urls.py` in `seafile_keeper_ext/seafile-server-latest/seahub/keeper/` provides the encapsulation point inside the extension.

**Note:** Using only `re_path(r'^keeper/', include('keeper.urls'))` would nest it as `/keeper/account/migrate/` (avoid for this feature).

After merge and extension redeploy (or full), restart seahub on APP nodes.

See the in-tree `seafile_keeper_ext/scripts/migration/README.md` for more. The root `PR_example_*` files remain as reference.

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