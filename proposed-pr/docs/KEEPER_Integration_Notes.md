# Integration Notes for Self-Service Email Migration

## 1. App Registration
The `keeper.migration` app should be available. In `seahub_settings.py` or via the extension mechanism, ensure it can be imported (the package has `apps.py` with `MigrationConfig`).

Example in settings if needed:
```python
# In the KEEPER extension loading
INSTALLED_APPS += ['keeper.migration']
```

## 2. URL Configuration
Add the migration URLs so the page is easily linkable from banners, help, and emails.

Recommended (add near other account/keeper includes in your main seahub/urls.py or the KEEPER extension's url loading):

```python
from django.urls import path, include

urlpatterns += [
    # Recommended: direct include for /account/migrate/
    path('account/migrate/', include('keeper.migration.urls')),

    # Alternative (if you want the whole keeper package):
    # path('keeper/', include('keeper.urls')),
]
```

After this change the self-service screen lives at `/account/migrate/`.

See:
- `proposed-pr/docs/example_main_urls.py` (fuller example)
- `proposed-pr/docs/example_url_include.patch` (copy-paste version)
- `seafile_keeper_ext/seafile-server-latest/seahub/keeper/urls.py` (the package-side example included in the PR)

Apply this in your real KEEPER source before the next web redeploy.

## 3. Templates (required for visual match)
The three templates are at:
`seahub-data/custom/templates/keeper/migration/{landing,confirm,status}.html`

They currently do `{% extends "base.html" %}` + have `{% block extrahead %}` that loads the migration CSS.

To integrate:

1. Change the `extends "base.html"` line in all three files to the real base template your KEEPER deployment uses for logged-in pages (the one that already pulls keeper_*.css and your custom header/footer).

2. Make sure the following are loaded (either in the base or via the extrahead block in these templates):
   - Your normal `keeper_*.css` files (for overall KEEPER look)
   - The new `keeper-migration.css`:
     ```html
     <link rel="stylesheet" href="/media/custom/css/keeper-migration.css">
     ```

3. The templates already contain the prominent identity banners and the .migration-check-reminder note. Keep the banners very visible (distinct colors for SOURCE vs TARGET).

4. Optionally pull in other custom pieces the base normally provides:
   ```html
   {% include "keeper_footer.html" ignore missing %}
   ```

See the comments at the top of each .html file in `seahub-data/custom/templates/keeper/migration/` for the exact lines to change.

For a complete, copy-paste-ready checklist of exactly what to edit in your real KEEPER source for this step, see `docs/STEP1_KEEPER_web_integration.md`.

Do this change in your real KEEPER source tree (under seahub-data/custom) before the next redeploy of the web part. The files in the PR are the "delta" you apply on top of your existing custom templates.

## 4. User Email Resolution
The `_get_current_user_email` helper in views.py prefers `contact_email` (for SSO users) then falls back, matching the logic in the existing `migrate_account.py` / `seafile_common.py`. This should work with your Shibboleth/ADFS setup.

## 5. Notifications
The web side sends plain emails (with links and check-the-box instructions) on code generation and confirmation.
The worker sends result emails (success or problem) with the direct move link.

Hook these into your existing email system (post_office, or the same mechanism used by Seafile for account emails) when ready.

For the initial rollout, the move screen + manual ops monitoring is sufficient.

## 6. Admin & Management Commands
The data moves are registered in Django admin under the keeper section. Operators can search by email, filter, and use the "mark as failed" action.

Additionally, a management command is provided:
    python manage.py list_migration_requests [--status pending,in_progress]
Run it from the seahub context for quick CLI monitoring.

## 7. Linking the screen
Add prominent links to `/account/migrate/` from:
- Login page / dashboard banners (especially during email migration waves)
- Help center / knowledge base
- Pre-migration communication emails
- Post-login notifications for users who have a pending move

The screen is designed to be safe even if reached accidentally (it always shows the current logged-in identity and role).

## 8. Redeploy
Place the migration ops scripts in `seafile_keeper_ext/scripts/migration/` (as done in this PR). On `deploy-all` / redeploy of the scripts dir, they will land in `/opt/seafile/scripts/migration/`.

The table is in `keeper-db.sql` so new deploys/upgrades get it.

For existing systems, run the create sql manually (see the README in the migration dir).

## 9. Testing
- Test as source: generate code.
- Test as target: paste, confirm with all boxes.
- Test regenerate.
- Test the move screen for both roles.
- Test the worker picking up a move (use --dry-run first).
- Verify the identity banner is always correct (different logins).
- Verify that emails and pages instruct users to verify the identity banner and log out/login with the correct email if the indicated role (SOURCE/TARGET) is wrong.

## 10. Security notes for review
- All views are @login_required.
- The secret code is single-use for claim, bound to specific target at generation.
- Source can only generate/regenerate while logged in as source.
- Target can only claim while logged in as target.
- Strong confirmation checkboxes on target side.
- Code expiry enforced.

Rate limiting and additional audit can be added later.

## 11. Optional Configuration (future exposure)

The migration code has built-in defaults for:
- KEEPER_MIGRATION_CODE_LIFETIME_DAYS = 7
- KEEPER_MIGRATION_PAGE_URL = 'https://keeper.mpdl.mpg.de/account/migrate/'
- KEEPER_MIGRATION_SUPPORT_EMAIL = 'keeper@mpdl.mpg.de'

(We might document example settings in `seahub_settings.py` later when exposing for configuration. No changes required today. The keys are already supported in the code via Django settings.)
