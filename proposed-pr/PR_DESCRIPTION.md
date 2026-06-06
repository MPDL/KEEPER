# PR: Self-Service Email Account Migration for KEEPER

## Summary

Adds a user-triggered self-service flow for migrating KEEPER accounts from an old email identity to a new one (driven by institutional email changes such as MaxIT).

Users log into source → get code on `/account/migrate/` (with very prominent "current account = SOURCE" banner) → log into target → paste code after checking the banner (prominent "current account = TARGET" banner) → strong multi-step confirmation with irreversible warnings and required checkboxes → move logged → worker processes using the **existing** `migrate_account.py` logic (no changes to the proven migration pipeline).

This dramatically reduces operational load while preserving all safety guarantees (shares, groups, password copy, keeper-specific migration, deactivation, etc.).

## Key Changes

### Web / Application (KEEPER PR)
- New Django app `keeper.migration` with model, admin, views, urls, and templates.
- Table definition added directly to `keeper-db.sql`.
- Landing screen `/account/migrate/` that is context-aware (source vs target) and forces clear identity display.
- Full flow: get code (with basic rate limit + self-migration prevention), claim after banner check, strong confirm, move status screen.
- Templates designed to be styled with existing KEEPER custom CSS/branding for visual consistency.
- Integration notes and suggested URL include point.

### Ops / Automation
- New worker `process_keeper_email_migrations.py` that polls the table and calls the **existing** `migrate_account.py` as a subprocess (same pattern as the legacy bulk_migrate).
- Consolidated under `/opt/seafile/scripts/migration/` (with placeholders/copies of the original scripts for convenience).
- Includes `create_...sql` for the table (run manually on existing systems or via redeploy).
- Enhancements in worker: exclusive lock (no overlapping runs), stuck job recovery, notification hook, `--list-pending` CLI for manual ops. Includes run_migration_worker.sh wrapper.
- Django admin + management command `list_migration_requests` for monitoring.
- Scripts placed in `seafile_keeper_ext/scripts/migration/` (and the new `deploy-migration.sh` + small wiring in `build.py`/`keeper_setup.sh`) so normal KEEPER redeploys (via keeper_setup.sh / build.py) or the targeted `deploy-migration` commands will deliver the worker + create sql + support scripts (including wrapper) to the correct location. The 1-parameter design lets the same script act as "slipstreamed via build" or fully standalone.

### Safety & UX
- Extremely prominent current logged-in email + explicit SOURCE / TARGET role on every screen.
- The secret code is cryptographically random, 7-day lifetime, single-use for claim, bound to the pair.
- Strong confirmation on target side (multiple required checkboxes about deactivation and client reconfig).
- Regenerate supported for source.
- No user cancel (per requirements).

## Deployment Notes

- **DB**: Table is in `keeper-db.sql`. For existing systems, run the create sql manually (see `opt/seafile/scripts/migration/README.md`).
- **Worker + migration support scripts**: Deploy the contents of `scripts/migration/` (or let redeploy do it). New dedicated targeted deploy script `deploy-migration.sh` (1 param: `standalone` or `slipstream` / "via build") + `keeper_setup.sh deploy-migration` + `python build.py deploy --migration` for safe overlay on already-deployed KEEPER instances. Set up cron + DB creds in .env for the worker. Point `MIGRATION_SCRIPT_DIR` to the dir containing your `migrate_account.py`.
- **UI**: Deploy the KEEPER code change (plus the custom/ CSS+templates via the migration deploy paths). The `/account/migrate/` route must be registered by adding a direct include in the main `seahub/seahub/urls.py` (see `PR_example_main_urls.py` and the note in `seafile_keeper_ext/scripts/migration/README.md`). Link to `/account/migrate/` from banners, help, emails, etc.
- The worker continues to use the exact same migration logic as before.

## Testing / Rollout

- Pilot with a small group.
- Monitor via Django admin (search by email).
- Legacy bulk path remains available for mass waves.

## Files Changed (high level)

See the proposed structure in this repo for the full delta.

- New migration app + templates + keeper-db.sql addition (including `keeper/urls.py` for encapsulation)
- Ops worker + supporting scripts + docs
- Includes the actual change to core `seahub/seahub/urls.py` (in addition to the encapsulation in `keeper/urls.py`)
- Updated examples (`PR_example_main_urls.py`, `.patch`) and in-tree READMEs (now the PR itself wires the URL)
- Operational docs (SOP, integration notes, STEP1 checklist, banner examples) are provided alongside this PR for pilots and deployment (not included in the repo tree).

## Related

- Original manual process SOP remains for bulk/exception cases.
- Design doc (in this workspace) with all decisions (code 7 days + regenerate, keeper-db, manual sql run, English only, no user cancel, pipeline stays on automation host, etc.).

This is ready to submit as a PR **against the keeper_7.0-sso deployment branch**.

The feature (UI + worker + targeted deploy script) is complete and adapted:
- URLs use re_path + from django.urls (to match current style on keeper_7.0-sso)
- keeper-db.sql is the branch version with our table appended (not a replacement)
- New deploy-migration.sh (single param slipstream|standalone) + connected to build.py (--migration) and keeper_setup.sh (deploy-migration target) for safe "on top of already deployed" installs.
- The PR now includes the central change to `seahub/seahub/urls.py` (direct `re_path(r'^account/migrate/', include('keeper.migration.urls'))` added in the KEEPER custom URLs section for the self-service migration page). This means after merge, `/account/migrate/` will be wired without additional manual patching of core urls (though seahub restart on APP nodes is still needed, and custom templates/CSS via seahub-data or the extension).
- Legacy migrate_account untouched, etc. All other decisions preserved.

Detailed integration steps (STEP1 etc.) and pilot materials are in the accompanying local checklists (removed from this PR tree per prior request).