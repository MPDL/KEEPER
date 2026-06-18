from django.apps import AppConfig


class MigrationConfig(AppConfig):
    name = 'keeper.migration'
    verbose_name = "KEEPER Self-Service Email Migration"
    # The app provides the /account/migrate/ self-service flow and the DB model
    # for tracking moves. The actual heavy lifting is done by the ops worker
    # in /opt/seafile/scripts/migration/ using the existing migrate_account.py.