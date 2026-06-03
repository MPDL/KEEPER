"""
URL configuration for the self-service KEEPER email migration app.

In the full KEEPER integration, include this from the main seahub or keeper URLs, e.g.:
    path('account/migrate/', include('keeper.migration.urls')),
"""

from django.urls import path
from . import views

# Names are prefixed with keeper_migration_ for easy global use.
# When including, you can do:
# path('account/migrate/', include('keeper.migration.urls'))
# Then use {% url 'keeper_migration_landing' %} etc.

urlpatterns = [
    path('', views.migration_landing, name='keeper_migration_landing'),
    path('status/<int:pk>/', views.migration_status, name='keeper_migration_status'),
    path('confirm/<int:pk>/', views.confirm_migration, name='keeper_migration_confirm'),
]