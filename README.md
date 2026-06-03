# keeper-email-migration

This workspace is the development home for the **Self-Service Email Account Migration** feature for KEEPER (the MPDL/Max Planck Seafile-based research data platform).

## Purpose

Transform the current operator-driven migration process (`migrate_account.py`, `bulk_migrate.py`, etc.) into a safe, user-initiated self-service experience that still uses the proven migration pipeline on the automation host.

**Reference material** (original automation work):
- `\\?\C:\Users\peterfi\update_seafile_token\` (especially `migrate_account.py`, `seafile_common.py`, `SOP_Keeper_Account_Migration.md`, `CLAUDE.md`)

## Current State of This Repo

- `docs/self-service-email-migration-design.md` — **Polished design document** (authoritative decisions captured)
- `proposed-pr/` — Directory structure + starter files that mirror what will go into a PR against https://github.com/MPDL/KEEPER
- Detailed implementation task list (visible in the agent's todo system)

## Key Decisions (Confirmed)

- Migration table → **keeper-db** (via existing `DbRouter`)
- Token lifetime → **7 days**, **regenerate supported**
- Users **cannot cancel** pending requests
- Notifications → **Email + in-app** (where practical)
- Heavy migration pipeline **stays on the automation host**; background worker polls the DB
- All user-facing text → **English only**

## How to Work Here

1. Read the design document first.
2. Use the detailed phased task list (the agent maintains it via the todo system).
3. Develop changes under `proposed-pr/` so they can be cleanly mapped to the KEEPER repo paths.
4. When ready, the contents of `proposed-pr/` + the design doc become the basis of the actual pull request.

## Useful Commands (Windows/PowerShell)

```powershell
# View current task status (via agent)
# The agent uses todo_write / todo_read under the hood

# When editing proposed files, keep paths relative to the KEEPER repo layout
```

## Current Status

**The proposed-pr/ tree is ready to form the basis of a PR to https://github.com/MPDL/KEEPER.**

**Ops / Automation side (complete, ready to deploy manually or via redeploy):**
- Full worker + create table sql + original scripts as placeholders under the migration dir.
- Worker enhancements: lock, stuck recovery, notification hook, `--list-pending` for manual listing. Includes run_migration_worker.sh wrapper.
- Redeploy support: files also in `seafile_keeper_ext/scripts/migration/` so `keeper_setup.sh` / `build.py deploy --all` will deliver them to `/opt/seafile/scripts/migration/`.
- Django management command `list_migration_requests` for admins (deployed with the KEEPER code).
- Custom CSS for migration page (keeper-migration.css).
- Manual SQL run documented (per your preference).
- Dedicated STEP1/STEP2/etc. checklists prepared in both the proposed tree and your real update_seafile_token/ dir.

**Web / KEEPER PR side (core UI flow implemented + polished + integration docs ready):**
- Table directly in `keeper-db.sql`.
- Model + admin + management command `list_migration_requests`.
- Full basic self-service flow (landing with generate/claim/regenerate + rate limit, strong confirm with checkboxes, status).
- Templates polished with KEEPER panel structure, banners, footer includes, and detailed integration comments.
- URLs + example include patch + settings placeholder (minimal, defaults builtin).
- Prominent SOURCE / TARGET identity banners on every page + on-screen reminders.
- Full integration instructions + STEP1 checklist for web wiring (base template, CSS, URL include) in docs/.

**Docs:**
- Design doc (phases updated to complete)
- New self-service SOP
- KEEPER integration notes (with future config note)
- PR description ready (wording feedback section removed; user confirmed good)
- STEP1_KEEPER_web_integration.md (new dedicated checklist for the integration step you are on)

**Remaining (deployment/pilot steps on your side, fully documented):**
- See the updated list in this README ("Next steps to pilot / production").
- Wording for users is settled (plain but professional for European scientists).
- Step 1 (web integration prep/docs) complete.

**Docs:**
- Design doc
- New self-service SOP
- KEEPER integration notes
- PR description ready

**Next steps to pilot / production (the feature core is complete in `proposed-pr/`):**

**1. KEEPER web integration (in the KEEPER source tree, before web redeploy):**
   - Apply the URL include for `/account/migrate/` (see `proposed-pr/docs/example_main_urls.py` or `example_url_include.patch` into your main seahub/urls.py or equivalent).
   - In the migration templates (`seahub-data/custom/templates/keeper/migration/*.html`): replace `{% extends "base.html" %}` with the real KEEPER base used for authenticated pages.
   - Load `seahub-data/custom/keeper_*.css` + `keeper-migration.css` (templates have detailed comments; see also `KEEPER_Integration_Notes.md` section 3).
   - Optionally register the `keeper.migration` app if your extension loader requires it.

**2. Ops / automation host setup (for the worker):**
   - Place the scripts under `/opt/seafile/scripts/migration/` (copy from `proposed-pr/opt/seafile/scripts/migration/` for manual pilot, or rely on redeploy from `seafile_keeper_ext/scripts/migration/` via keeper_setup.sh / build.py).
   - Run the manual `CREATE TABLE` (your preference; SQL in `create_keeper_email_migration_table.sql` or via `keeper-db.sql` on new deploys).
   - Configure `.env` (KEEPER_DB_*, MIGRATION_SCRIPT_DIR, EMAIL_* for worker notifications, MIGRATION_PAGE_URL, MIGRATION_ALWAYS_CREATE if desired).
   - Set up the cron (example in worker README and script header: `*/5 * * * * cd ... && python3 process...`).
   - (For your local pilot) you can populate `C:\Users\peterfi\update_seafile_token\migration\` from the proposed tree.

**3. Deploy + promote the page:**
   - Deploy the KEEPER code change (brings the UI, management command, etc.).
   - Add the promotion banner text (from `proposed-pr/docs/example_user_banner.txt` or the version in your real SOP dir) to login/dashboard/help pages during waves.

**4. Pilot & observe:**
   - Full end-to-end: source generates code → target claims + confirms (with banner checks) → worker picks up and calls the untouched `migrate_account.py` → notifications fire → user reconfigures clients.
   - Monitor via Django admin, `python manage.py list_migration_requests`, or worker `--list-pending` / `--dry-run`.
   - Use the updated self-service section in your real `SOP_Keeper_Account_Migration.md`.

**5. Polish / follow-ups (after pilot feedback):**
   - Wire real email sending if the current `django.core.mail.send_mail` (web) + smtplib (worker) doesn't match your production setup (e.g. post_office, specific from_email).
   - Improve rate limiting (current is simple per-user 60s session-based; see comments in views.py).
   - Any final wording tweaks from real European scientist users.
   - Optional: better stuck-job alerting, more worker CLI flags.

The dedicated `proposed-pr/docs/SOP_Keeper_SelfService_Account_Migration.md` has the merged user + ops view (you've been syncing the key parts into the real legacy SOP).

See `proposed-pr/PR_DESCRIPTION.md` for the PR summary text.

See `docs/self-service-email-migration-design.md` and `proposed-pr/docs/KEEPER_Integration_Notes.md` for the authoritative plan + detailed integration steps (templates comments also have the "replace base + load CSS" instructions).

The core (UI + worker calling the proven legacy pipeline unchanged + plain-language safety) is complete and ready for the above deployment steps.

## Doing the actual PR (with token)

A helper script has been prepared on the feature branch:

```powershell
.\prepare-and-open-pr.ps1 -GithubToken "ghp_yourtokenhere" -GithubUsername "yourgithubusername"
```

It will:
- Fork MPDL/KEEPER under your account (if not already)
- Push this branch to your fork
- Open the PR using the content from `proposed-pr/PR_DESCRIPTION.md`

Once you provide the token + username, I can run the script for you (or you can run it yourself). The token only needs `repo` (or `public_repo`) scope.

---

**Workspace initialized:** 2026-06-01  
**Status:** proposed-pr/ ready for PR. Step 1 (web integration prep) complete. See "Next steps to pilot / production" above.