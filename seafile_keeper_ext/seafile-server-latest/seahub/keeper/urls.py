"""
URLs for the keeper package.

NOTE: This urls.py did not exist prior to the self-service email migration feature.
It is being added as part of this PR to encapsulate KEEPER-specific URL routing inside the
keeper app (instead of directly patching the core seahub/seahub/urls.py for every new feature).

To integrate the self-service migration:

In your main seahub/urls.py (on the keeper_7.0-sso branch and later) or wherever KEEPER custom URLs are included, add something like:

    from django.urls import include, re_path
    ...
    re_path(r'^keeper/', include('keeper.urls')),

Or more specifically for the migration page (recommended for easy linking):

    re_path(r'^account/migrate/', include('keeper.migration.urls')),

The migration screen will then be at /account/migrate/ (easy to link from emails, help areas, banners, etc.).

Make the banner very visible with current user email + "SOURCE" or "TARGET" role.
"""

from django.urls import re_path, include

urlpatterns = [
    # Self-service migration screen (easy to link: /account/migrate/ or via this)
    re_path(r'^account/migrate/', include('keeper.migration.urls')),

    # Other keeper-specific URLs can be added here
]