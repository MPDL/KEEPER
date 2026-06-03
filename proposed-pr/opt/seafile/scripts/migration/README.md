# KEEPER Email Migration Scripts

Location: `/opt/seafile/scripts/migration/`

## Scripts in this directory

- `process_keeper_email_migrations.py` — New self-service migration worker (polls `keeper_email_migration` table and drives the existing migration logic).
- `migrate_account.py` — Existing full account migration script (do not modify).
- `seafile_common.py` — Shared utilities for the above (do not modify).
- `requirements.txt` — Python dependencies for the worker and scripts.

## Deployment

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

5. Recommended cron (every 5 minutes):
   ```cron
   */5 * * * * cd /opt/seafile/scripts/migration && python3 process_keeper_email_migrations.py >> /var/log/keeper-migration-worker.log 2>&1
   ```

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

Additionally, to ensure the create sql (and migration ops scripts) are deployed to /opt/seafile/scripts/migration/ during normal KEEPER redeploys, they are included in the KEEPER source tree under `seafile_keeper_ext/scripts/migration/`. The deployment scripts (keeper_setup.sh deploy-all / build.py deploy --all) deploy the 'scripts' directory.

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