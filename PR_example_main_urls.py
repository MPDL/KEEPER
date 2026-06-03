# Example of how to include the KEEPER migration URLs in your main seahub/urls.py
# (or wherever you include KEEPER custom apps).
#
# After this change, the self-service page will be at https://your-keeper/account/migrate/
# (easy to link from banners, help, emails).

from django.conf.urls import url, include

# ... your other imports ...

# Add this near other KEEPER or account-related includes.
# Recommended: direct include for the migration screen (cleanest for linking).
urlpatterns = [
    # ... existing patterns ...

    # KEEPER self-service migration (recommended)
    url(r'^account/migrate/', include('keeper.migration.urls')),

    # Alternative: include the whole keeper package (if you want other keeper urls under /keeper/)
    # url(r'^keeper/', include('keeper.urls')),

    # ... rest of your urls ...
]

# Notes:
# - The migration screen is at /account/migrate/
# - It uses prominent SOURCE/TARGET identity banners on every page.
# - Link it from login banners, dashboard, help areas, pre-migration emails, etc.
# - Uses legacy url(r'...') style (like all other URLs in seahub/urls.py) for Django 1.11 compat.
# - See KEEPER_Integration_Notes.md for the full template base + CSS swap instructions.