# SOP: Keeper Self-Service Account Migration

**System:** KEEPER (Seafile-based) — MaxIT / MPDL  
**Version:** 2.0 (Self-Service)  
**Last Updated:** 2026-06 (updated for self-service account data transfer)  
**Owner:** Keeper Team

## 1. Purpose

This SOP describes the **self-service** process for migrating a user account in KEEPER from one email identity to another (e.g. as part of MaxIT email migration).

Users start it themselves on a screen using a code. The move happens using the normal tools.

The old IT-driven bulk process (using CSVs and direct calls to migrate_account.py) remains available for mass waves or exceptions.

## 2. User Flow

1. Log in with your old email address. Navigate to the account migration page (link provided in banners or help resources). Verify on the identity banner that the account is identified as SOURCE. Enter the target (new) email address and request a migration code (valid for 7 days).

2. Log in with your new email address. Return to the account migration page. Verify on the identity banner that the account is identified as TARGET. Enter the migration code received from the source account, review the information and required acknowledgments, check the confirmation boxes, and submit.

3. The transfer will be queued. You will receive an email notification. The email will direct you to the account migration page (with a direct status link) where you can verify the identity banner shows the correct role (SOURCE or TARGET) for the transfer. Log out and log in with the appropriate email if the banner is incorrect.

4. After completion, log in with the new email address and reconfigure your Seafile clients as needed. The old email address will have been deactivated for Keeper access.

**Important**: The identity banner on the migration page always displays the currently authenticated email address and its role (SOURCE or TARGET) in the transfer.

## 3. Prerequisites for rollout

- The feature is enabled (the needed table is ready, tools are in place after deploy).
- The link to the screen for moving your data is easy to find (in banners, help, emails).
- People can log in with both their old and new emails.

## 4. For Users (self-service)

The account migration page provides step-by-step guidance with appropriate warnings and confirmations.

You must be able to authenticate with both the old and new email addresses and have any passwords for encrypted libraries available.

After submitting the confirmation:
- Monitor progress via the account migration page or the notification email (which includes a direct link to the transfer status). The email and page will instruct you to verify the identity banner.
- After successful completion, log in with the new email address and reconfigure clients (reusing existing local folders where possible).

## 5. For Operators

- Use Django admin (under keeper migration) to monitor transfers, search by email, or manually mark a transfer as failed if required.
- The worker logs to daily files in `logs/` under the migration dir.
- For mass migrations: continue using the legacy `bulk_migrate.py` + CSV as before.
- To force a specific move: the worker will pick it up on next run, or you can run the worker manually with --dry-run first.

Manual table creation (if not yet applied via keeper-db.sql redeploy):

```bash
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS -P $DB_PORT keeper-db < /opt/seafile/scripts/migration/create_keeper_email_migration_table.sql
```

## 6. Rollback / Failure

- The worker uses the same proven logic as before (shares backup JSONs are still created by migrate_account.py).
- If a move fails, it is marked with a problem, error is stored, admin can see it.
- Source account is only deactivated on successful completion of the full pipeline.

## 7. Related Files (after deployment)

- `/opt/seafile/scripts/migration/process_keeper_email_migrations.py`
- `/opt/seafile/scripts/migration/create_keeper_email_migration_table.sql`
- `/opt/seafile/scripts/migration/migrate_account.py` (and common)
- In KEEPER code: `seahub/keeper/migration/` (views, models, templates)
- `seahub/keeper/keeper-db.sql` (table definition)

## 8. References

- Original SOP for the IT-driven process (keep for bulk cases).
- Design doc in the migration project repo.

Troubleshoot at client level first. Escalate server-side to keeper team.