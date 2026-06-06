# Example of the proper content to add to your main seahub/seahub/urls.py
# (the root URLconf, loaded via seahub.utils.rooturl on KEEPER).
# This is the "copy" you should use/edit on the server.
#
# keeper/urls.py (the new encapsulation file) is shipped for organization,
# but does NOT auto-activate routes. You must add the include here.
#
# The migration must be at /account/migrate/ (not /keeper/account/migrate/).
# So use the direct include (not just ^keeper/ include).

from django.urls import include, re_path

# ... your other imports ...

# Typical location: inside or near the existing KEEPER custom URLs block
# (there are already several re_path for doi, landing-page, bloxberg, archive, etc.)
urlpatterns = [
    # ... existing patterns ...

    # KEEPER self-service email migration (phone-move / self-service)
    # Direct include so the path is exactly /account/migrate/
    re_path(r'^account/migrate/', include('keeper.migration.urls')),

    # Example of other existing KEEPER urls (for reference, do not remove)
    # re_path(r'^doi/libs/...', DoiView...),
    # re_path(r'^landing-page/libs/...', ...),
    # re_path(r'^archive/...', ...),
    # re_path(r'^bloxberg-cert/...', ...),
    # re_path(r'^project-catalog/...', ...),
    # re_path(r'^client-login/...', ...),

    # If you also want to include the keeper package for future features:
    # re_path(r'^keeper/', include('keeper.urls')),
    # (Note: the migration is already covered by the direct line above, so no nesting issue.)

    # ... rest of your urls ...
]

# Notes:
# - The migration screen is at /account/migrate/
# - It uses prominent SOURCE/TARGET identity banners on every page.
# - Link it from login banners, dashboard, help areas, pre-migration emails, etc.
# - Uses re_path (matching the style in this branch's seahub/urls.py which mixes path() and re_path()).
# - After editing, restart seahub on APP nodes.
# - See KEEPER_Integration_Notes.md (or pilot STEP1) for the full template base.html + CSS swap instructions for custom templates.
# - Also deploy via deploy-migration.sh on APP (for templates/css + keeper/migration py package) and BG (for worker + cron + sql).