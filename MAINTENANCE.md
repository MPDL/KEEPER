# Maintenance notes — modifications to existing / upstream source files

This feature is mostly **additive** (a self-contained `keeper.migration` Django app,
worker scripts, a deploy script, templates and CSS). A few changes, however, modify or
**override existing files** — and those carry an upgrade-maintenance cost. They are listed
here so they can be re-checked after every Seafile/KEEPER upgrade.

## How the overlay works (why upgrades matter)
`python build.py deploy --all` copies the extension tree
(`seafile_keeper_ext/seafile-server-latest/...`) over the installed seahub, then runs
`make dist-keeper` (npm build) and `collectstatic`. Any file placed in the ext at an
upstream path **replaces** the upstream file at deploy time — there is no merge, the ext
copy wins. So when Seafile is upgraded, the upstream version of an overridden file may
change underneath our copy and must be re-reconciled.

## ⚠️ Upstream (Seafile) files — re-check on every Seafile upgrade

### 1. `frontend/src/settings.js` — FULL-FILE OVERRIDE (highest maintenance)
- **What:** the React entry for the `/profile/` user-settings page. We ship a *verbatim
  copy* of the upstream file with three additions: `import DataTransfer …`, a side-nav
  entry, and `<DataTransfer />` rendered under the Social Login / SAML section.
- **Why a full copy:** the page is a React SPA with no server-side or plugin hook for
  inserting a section, so the only way to add one is to override the page module and
  rebuild the bundle.
- **Risk:** the copy is pinned to Seafile **12.0.16**. After an upgrade, upstream changes
  to the settings page (new sections, refactors, prop changes) will **not** appear, and the
  override can break the page or silently drop new upstream functionality.
- **On upgrade:** diff the new upstream `settings.js` against this copy, re-apply only the
  three Data Transfer additions on top of the *new* upstream version, then rebuild the
  frontend (`build.py deploy --all`, Node required).
- The section component `frontend/src/components/user-settings/data-transfer.js` is
  **new/additive** (no upstream counterpart) and needs no reconciliation.

### 2. `seahub/seahub/urls.py` — MODIFIED (medium maintenance)
- **What:** adds `re_path(r'^account/migrate/', include('keeper.migration.urls'))` to the
  KEEPER block of the root URLconf so the page is reachable at `/account/migrate/`.
- **Risk:** a one-line include in an upstream file.
- **On upgrade:** if upstream rewrites this file, re-apply the include. (The route is
  encapsulated in `keeper/urls.py`, but the *root* URLconf must include it directly.)

## 🟢 KEEPER-owned files modified (low maintenance — KEEPER repo, not upstream Seafile)
These already belong to the KEEPER extension; they are edited, not overridden from Seafile,
so a Seafile upgrade doesn't disturb them. Keep the additions when regenerating/merging:
- `seafile_keeper_ext/build.py` — wires `deploy --migration` to `deploy-migration.sh`.
- `seafile_keeper_ext/keeper_setup.sh` — adds the `deploy-migration` target.
- `seafile-server-latest/seahub/keeper/__init__.py` — registers the migration app.
- `seafile-server-latest/seahub/keeper/keeper-db.sql` — appends the
  `keeper_email_migration` table DDL (keep the appended block).

## ✅ Additive — no upgrade concern
New paths that don't shadow any existing file (Seafile/KEEPER upgrades don't affect them
beyond normal API compatibility):
- `keeper/migration/` (models, views, urls, admin, apps), `keeper/urls.py`,
  `keeper/management/commands/list_migration_requests.py`
- `frontend/src/components/user-settings/data-transfer.js`
- `seahub-data/custom/templates/keeper/migration/*.html`,
  `seahub-data/custom/css/keeper-migration.css`
- `scripts/migration/*` (worker + helpers + `.env.example` + SQL),
  `deploy-migration.sh`, `system/cron.d.keeper-migration`

## Recommendation
After any seahub upgrade, **re-diff `frontend/src/settings.js` and `seahub/seahub/urls.py`
against the new upstream** and re-apply the deltas before rebuilding. Keep both deltas as
small as possible to make that reconciliation easy.
