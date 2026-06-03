# STEP 1: KEEPER Web Integration (apply in your real KEEPER source before redeploy)

This is the work needed in the KEEPER source tree (the one you build with keeper_setup.sh etc.).

Do these changes, then redeploy the web part.

## A. URL wiring (seahub urls)

Add the migration route so `/account/migrate/` works.

**Option 1 - Recommended (direct):**

In your main `seahub/urls.py` (or wherever KEEPER routes are included), add near other account includes:

```python
from django.urls import path, include

urlpatterns += [
    path('account/migrate/', include('keeper.migration.urls')),
]
```

**Option 2 - Via the keeper package:**

If you want everything under /keeper/ too, also add:

```python
urlpatterns += [
    path('keeper/', include('keeper.urls')),
]
```

See also:
- `docs/example_main_urls.py`
- `docs/example_url_include.patch` (copy-paste friendly version)
- `seafile_keeper_ext/seafile-server-latest/seahub/keeper/urls.py` (what the PR contributes on the package side)

After this the page is at `/account/migrate/`.

## B. Template base + CSS swap (visual match)

The three templates live in `seahub-data/custom/templates/keeper/migration/`.

They currently say `{% extends "base.html" %}`.

**What to do:**

1. In all three files (`landing.html`, `confirm.html`, `status.html`):
   - Change `{% extends "base.html" %}` to use your real KEEPER authenticated base (the one used for logged-in pages, the one that already includes your header, footer, and keeper_*.css).

2. Make sure these styles are loaded (add to the base or to the `{% block extrahead %}` in the three files):

```html
<link rel="stylesheet" href="/media/custom/css/keeper-migration.css">
```

(Your normal `keeper_*.css` should already be loaded by the real base.)

3. Optionally bring in other custom includes your base normally provides, e.g.:

```html
{% include "keeper_footer.html" ignore missing %}
```

Each template file has a big comment block at the top with the exact instructions.

The goal is that the migration screens look 100% native to the rest of KEEPER (same fonts, buttons, colors, layout, header/footer).

## C. App registration (if needed)

In your KEEPER extension loading / seahub_settings.py (or equivalent):

```python
INSTALLED_APPS += ['keeper.migration']
```

(See `seafile_keeper_ext/conf/seahub_settings.py` and the integration notes for the minimal version.)

## D. After these changes

- Redeploy the web part of KEEPER (the seahub-data/custom bits + any code changes).
- The page will be live at `/account/migrate/`.
- Proceed to step 2 (ops host / worker) and step 3 (banner + pilot).

See the main `KEEPER_Integration_Notes.md` for the complete checklist and the templates' own comments for the precise lines to edit.
