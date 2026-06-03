"""
URL configuration for the self-service KEEPER email migration app.

In the full KEEPER integration, include this from the main seahub or keeper URLs, e.g.:
    url(r'^account/migrate/', include('keeper.migration.urls')),
"""

from django.conf.urls import url
from . import views

# Names are prefixed with keeper_migration_ for easy global use.
# When including, you can do:
# url(r'^account/migrate/', include('keeper.migration.urls'))
# Then use {% url 'keeper_migration_landing' %} etc.

urlpatterns = [
    url(r'^$', views.migration_landing, name='keeper_migration_landing'),
    url(r'^status/(?P<pk>\d+)/$', views.migration_status, name='keeper_migration_status'),
    url(r'^confirm/(?P<pk>\d+)/$', views.confirm_migration, name='keeper_migration_confirm'),
]