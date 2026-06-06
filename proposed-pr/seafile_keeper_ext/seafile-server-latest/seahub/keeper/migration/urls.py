"""
URL configuration for the self-service KEEPER email migration app.

In the full KEEPER integration (keeper_7.0-sso+), include this DIRECTLY from the main
seahub/seahub/urls.py (the root URLconf loaded by seahub.utils.rooturl), e.g.:

    from django.urls import include, re_path
    ...
    re_path(r'^account/migrate/', include('keeper.migration.urls')),

Do not rely solely on including 'keeper.urls' under a ^keeper/ prefix (see the docstring
in keeper/urls.py), as that would cause incorrect nesting. The page must live at
/account/migrate/ for easy linking from emails/banners.
"""

from django.urls import re_path
from . import views

# Names are prefixed with keeper_migration_ for easy global use.
# When including, you can do:
# re_path(r'^account/migrate/', include('keeper.migration.urls'))
# Then use {% url 'keeper_migration_landing' %} etc.

urlpatterns = [
    re_path(r'^$', views.migration_landing, name='keeper_migration_landing'),
    re_path(r'^status/(?P<pk>\d+)/$', views.migration_status, name='keeper_migration_status'),
    re_path(r'^confirm/(?P<pk>\d+)/$', views.confirm_migration, name='keeper_migration_confirm'),
]