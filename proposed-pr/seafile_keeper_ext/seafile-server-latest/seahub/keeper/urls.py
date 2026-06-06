"""
URLs for the keeper package.

NOTE: This urls.py did not exist prior to the self-service email migration feature.
It is being added as part of this PR to encapsulate KEEPER-specific URL routing inside the
keeper app (instead of directly patching the core seahub/seahub/urls.py for every new feature).

However, this file by itself does NOT register any routes. You must explicitly include
it (or the migration sub-module) from the *main* seahub/seahub/urls.py (the one loaded
by seahub.utils.rooturl).

Recommended (cleanest, no wrong nesting):

    from django.urls import include, re_path
    ...
    re_path(r'^account/migrate/', include('keeper.migration.urls')),

If you want to namespace other future keeper features:

    re_path(r'^keeper/', include('keeper.urls')),

NOTE: If you do the ^keeper/ include, the migration is still best added via the direct
^account/migrate/ line above (otherwise it would incorrectly become /keeper/account/migrate/).

The migration screen will then be at /account/migrate/ (easy to link from emails, help areas, banners, etc.).

Make the banner very visible with current user email + "SOURCE" or "TARGET" role.
"""

from django.urls import re_path, include

urlpatterns = [
    # Self-service migration screen (easy to link: /account/migrate/).
    # This is provided here for encapsulation, but the actual registration must be
    # done via direct include in the root seahub/seahub/urls.py (see docstring above).
    re_path(r'^account/migrate/', include('keeper.migration.urls')),

    # Other keeper-specific URLs (future) can be added here.
    # If included via ^keeper/ from main urls.py they will live under /keeper/...
]