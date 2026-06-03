"""
URLs for the keeper package.

To integrate the self-service migration:

In your main seahub/urls.py or wherever KEEPER custom URLs are included, add something like:

    from keeper import urls as keeper_urls
    url(r'^keeper/', include(keeper_urls)),

Or more specifically for the migration page (recommended for easy linking):

    from keeper.migration import urls as migration_urls
    url(r'^account/migrate/', include(migration_urls)),

The migration screen will then be at /account/migrate/ (easy to link from emails, help areas, banners, etc.).

Make the banner very visible with current user email + "SOURCE" or "TARGET" role.
"""

from django.conf.urls import url, include

urlpatterns = [
    # Self-service migration screen (easy to link: /account/migrate/ or via this)
    url(r'^account/migrate/', include('keeper.migration.urls')),

    # Other keeper-specific URLs can be added here
]