# KEEPER Email Migration Scripts

Location: `/opt/seafile/scripts/migration/`

## Scripts in this directory

- `process_keeper_email_migrations.py` — New self-service migration worker (polls `keeper_email_migration` table and drives the existing migration logic).
- `migrate_account.py` — Existing full account migration script (do not modify).
- `seafile_common.py` — Shared utilities for the above (do not modify).
- `requirements.txt` — Python dependencies for the worker and scripts.

## Deployment

You can deploy the migration components in several ways. The dedicated `deploy-migration.sh` (and `keeper_setup.sh deploy-migration`) exist specifically to allow safe overlay on an *already deployed* KEEPER instance without re-deploying unrelated scripts or configs.

### Option A: Targeted migration-only deploy (recommended for updates / pilot on existing systems)

From the `seafile_keeper_ext` checkout dir:

```bash
# Interactive, with prompts before overwriting (standalone mode)
./deploy-migration.sh standalone

# Or via the extended keeper_setup.sh (also standalone mode)
./keeper_setup.sh deploy-migration
```

This copies (the script is role-aware based on __NODE_TYPE__ from your keeper*.ini):
- On BACKGROUND nodes: `scripts/migration/*` (the worker + legacy tools) → `/opt/seafile/scripts/migration/`
- On APP nodes: `seahub-data/custom/templates/keeper/migration/*` + `css/keeper-migration.css` (the /account/migrate/ UI) + the keeper/migration Python package into the installed seahub (so the frontend views work)

**Web UI URL registration (included via the KEEPER PR)**

The PR includes the change to the core `seahub/seahub/urls.py` (direct include for the migration at `/account/migrate/`).

See `seafile_keeper_ext/seahub/keeper/urls.py` (encapsulation) and the proposed core change in the PR materials.

After deploying the extension (or full redeploy) and the central urls update is merged, restart seahub on APP nodes to activate the `/account/migrate/` page (with SOURCE/TARGET banners).

(The root `PR_example_main_urls.py` and `.patch` are still available as reference for the exact addition in the KEEPER block.)

### Option B: Full redeploy (brings everything including migration)

```bash
# Full (will also deploy other scripts/, seahub-data/, seafile-server-latest etc.)
./keeper_setup.sh deploy-all

# Or using build.py (the --migration flag is also wired here for the targeted path)
python build.py deploy --all
python build.py deploy --migration     # only the migration bits, slipstream mode (non-interactive)
python build.py deploy -d scripts/migration seahub-data/custom   # low-level alternative
```

### Option C: Manual / pilot copy

1. Ensure this directory exists on the automation / management host:
   ```bash
   mkdir -p /opt/seafile/scripts/migration
   ```

2. Copy the scripts into it (or rsync from your source).

3. Install dependencies (once):
   ```bash
   cd /opt/seafile/scripts/migration
   pip3 install -r requirements.txt
   ```

4. Create / update `.env` in this directory (or ensure variables are in the environment):
   ```env
   KEEPER_DB_HOST=...
   KEEPER_DB_PORT=3306
   KEEPER_DB_NAME=keeper-db
   KEEPER_DB_USER=...
   KEEPER_DB_PASSWORD=...

   MIGRATION_SCRIPT_DIR=/opt/seafile/scripts/migration

   # Optional
   # MIGRATION_ALWAYS_CREATE=0

   # Email settings for notifications (from .env; the worker has built-in defaults)
   # EMAIL_HOST=smtp.example.com
   # EMAIL_PORT=587
   # EMAIL_USE_TLS=true
   # EMAIL_HOST_USER=...
   # EMAIL_HOST_PASSWORD=...
   # DEFAULT_FROM_EMAIL=keeper@mpdl.mpg.de
   # SUPPORT_EMAIL=keeper@mpdl.mpg.de
   # MIGRATION_PAGE_URL=https://keeper.mpdl.mpg.de/account/migrate/   # base for links in notification emails (worker default)
   # Emails and the web screens tell users: go to the page, check the top banner shows the correct (SOURCE or TARGET) account, logout/login if needed.
   ```

5. Cron setup:
   The cron job is deployed automatically when you run `deploy-migration.sh` (or `build.py deploy --migration` / `keeper_setup.sh deploy-migration`) on a BACKGROUND node.
   It installs to `/etc/cron.d/cron-keeper-migration` (every 5 min).
   No manual crontab edit is needed. You can verify with `cat /etc/cron.d/cron-keeper-migration` after deploy.

6. Test first with dry-run:
   ```bash
   cd /opt/seafile/scripts/migration
   python3 process_keeper_email_migrations.py --dry-run
   ```

7. List pending requests manually (no DB changes):
   ```bash
   python3 process_keeper_email_migrations.py --list-pending
   ```

8. Use the wrapper for convenience (loads .env):
   ```bash
   ./run_migration_worker.sh --dry-run
   ```

## Notes

- This worker calls the **existing** `migrate_account.py` via subprocess. No changes were made to the core migration logic.
- Logs for individual migrations go into the `logs/` subdirectory.
- The table `keeper_email_migration` lives in the `keeper-db` database (not the main seahub database).

### Schema change location

The table definition is committed **directly** to the KEEPER codebase here:

- `seafile_keeper_ext/seafile-server-latest/seahub/keeper/keeper-db.sql` (in the PR against MPDL/KEEPER)

For convenience when deploying just the operational scripts (without a full KEEPER code upgrade), a standalone copy is provided in this directory:

- `create_keeper_email_migration_table.sql`

Additionally, to ensure the create sql (and migration ops scripts) are deployed to /opt/seafile/scripts/migration/ during normal KEEPER redeploys, they are included in the KEEPER source tree under `seafile_keeper_ext/scripts/migration/`. The deployment scripts (keeper_setup.sh deploy-all / build.py deploy --all / the new deploy-migration.sh) deploy the 'scripts' directory (or just the migration sub-part).

Run the create_ version directly against the keeper-db when rolling out the worker on an existing installation.

**Manual table creation (as you will run it):**
```bash
# Example (adjust host/user/pass/db name from your keeper*.ini or env)
mysql -h ${__DB_HOST__} -u ${__DB_USER__} -p${__DB_PASSWORD__} -P ${__DB_PORT__} keeper-db \
  < /opt/seafile/scripts/migration/create_keeper_email_migration_table.sql
```

After the table exists, the worker can create rows via the web UI and process them.

After KEEPER code redeploy, you can also use the Django management command for monitoring:
    python manage.py list_migration_requests
(from the seahub context with KEEPER settings loaded).

The schema lives in the 'keeper' database (routed via keeper.dbrouter.DbRouter).

See the design document for more context.

See the main design document in the keeper-email-migration workspace for full context.

## Pilot / manual testing (before web UI is deployed)

For early testing of the worker + legacy pipeline (e.g. on an ops host or locally):

1. Ensure the `keeper_email_migration` table exists in keeper-db (run `create_keeper_email_migration_table.sql` manually if needed).

2. Seed a test row manually (example - replace emails and use a real token value):

```sql
INSERT INTO keeper_email_migration
  (source_email, target_email, migration_token, status, token_expires_at, requested_at, metadata)
VALUES
  ('old-email@example.org',
   'new-email@example.org',
   'PASTE_A_REAL_TOKEN_HERE_OR_USE_SECRETS_GENERATED_ONE',
   'pending',
   DATE_ADD(NOW(), INTERVAL 7 DAY),
   NOW(),
   JSON_OBJECT('pilot', true));
```

3. Run with your .env loaded:

```bash
cd /opt/seafile/scripts/migration
python3 process_keeper_email_migrations.py --dry-run
python3 process_keeper_email_migrations.py --list-pending
# live run (no --dry-run) will call the existing migrate_account.py --from ... --to ... --apply
```

On Windows for local pilot the equivalent commands use `python` or `py`.

After the web integration (see the STEP1_KEEPER_web_integration.md checklist provided with the PR materials), prefer using the self-service UI to generate real codes instead of manual INSERTs. The worker will consume rows created by the UI exactly the same way.
