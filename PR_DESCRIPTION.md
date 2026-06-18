# PR: Self-Service Data Transfer (email / SSO account migration) for KEEPER

## Summary

Adds a user-triggered, self-service flow that lets a KEEPER user move all their data
(libraries, shares, group roles, Keeper catalog/CDC/DOI/archive ownership) from one
account to another — without operator intervention. It is driven by the move to SSO/SAML
across MPG: since Seafile 11, SSO logins create accounts under an internal
virtual id (`uuid@auth.local`) rather than reusing the email, so users often land on a new,
empty account while their data stays on their original account.

The web app only **creates and observes** requests; the heavy migration still runs on the
automation host via the existing `migrate_account.py` (the proven pipeline is preserved).

## Supported cases
1. **Old, pre-Seafile-11 accounts** — email-as-id with a local password; SSO creates a separate
   `uuid@auth.local` account beside them.
2. **Accounts whose SSO email/credentials differ** from the original (e.g. an institute email
   domain change), so SSO resolves to a different/new account.

## User flow
- **Different-email transfer:** source logs in → generates a 7-day code on `/account/migrate/`
  (shown on screen with a copy button + emailed) → target logs in → pastes the code → strong
  multi-step confirmation (irreversible warnings + required checkboxes) → queued → worker runs.
- **Same-email (SSO) transfer:** a single checkbox — "I have another account with the same email
  address". The user (signed in with *either* account) ticks it; the system finds the counterpart
  account that shares the email and lets them **self-confirm in one session** (no emailed code, no
  second login). Data always moves old-account(data) → SSO account.
- Every screen shows a prominent **SOURCE / TARGET** identity banner.
- Status is shown **inline on `/account/migrate/`** for every state (pending / in progress /
  completed / failed) — there is no separate status page.

## Key changes

### Web / application (`keeper.migration`)
- New Django app: model (`EmailMigrationRequest`), admin, views, urls, templates; table in `keeper-db.sql`.
- Context-aware `/account/migrate/` landing (source vs target vs neutral), with the identity banner.
- Generate (with rate limit, self-migration block, and a **target-account-must-already-exist** check),
  regenerate, **cancel while pending** (deletes the request), claim, strong confirm.
- **Same-email SSO self-confirm**: finds the counterpart account by shared email and a **reliable
  SSO check** (the actual SAML binding in `social_auth_usersocialauth`, not the `@auth.local` name);
  records the **exact account ids** (so `migrate_account.py` resolves them unambiguously); works
  from either session.
- Status merged into the landing page; a **completed** transfer is shown for 48h, after which the
  page returns to the start state so a new transfer can begin.
- **`/profile/` integration**: a "Data Transfer" section added to the user settings page
  (`settings.js` React override) under Social Login / SAML, linking to `/account/migrate/`.

### Worker (`process_keeper_email_migrations.py`, BACKGROUND node)
- Polls only **confirmed** pending rows (`confirmed_at IS NOT NULL`) — confirmation gates processing.
- Calls the existing `migrate_account.py` as a subprocess (pipeline unchanged); lock, stuck-job
  recovery, `--dry-run`, `--list-pending`.
- **Auto-imports configuration** from `/opt/seafile/keeper-*.ini` (and Seafile `conf/.env`): DB
  credentials, SMTP, and the server URL — so a worker `.env` is optional. The only value normally
  required is `SEAFILE_AUTH_TOKEN`.

### Migration pipeline (minimal, backward-compatible)
- `migrate_account.py`: privileged steps run **locally (no SSH)** when the target is this host;
  remote SSH still works unchanged. `KEEPER_MIGRATE_SERVER`/`KEEPER_SSH_USER` are now optional.
- `seafile_common.get_user`: prefer an **exact account-id match** before contact_email, so an old
  account and an SSO account that share an email resolve deterministically.

### Deploy
- `deploy-migration.sh` (role-aware APP / BACKGROUND / SINGLE; **idempotent**), wired into
  `build.py deploy --migration` and `keeper_setup.sh deploy-migration`; cron + pip + idempotent table DDL.
- `.env.example` documents the pipeline variables and the auto-imported ones.

## Deployment notes
- **APP node:** deploy templates + the `keeper/migration` package; the `/profile/` section needs a
  frontend rebuild (`build.py deploy --all` / `generate --frontend`, Node required). Restart seahub.
- **BACKGROUND node:** deploy the worker; config auto-imports from `keeper-*.ini`. Set
  `SEAFILE_AUTH_TOKEN` in the worker `.env`.
- `/account/migrate/` is wired via a direct include in `seahub/seahub/urls.py`.

This targets the **`keeper_7.0-sso`** deployment branch and has been validated end-to-end on QA.
