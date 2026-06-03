"""Self-service email migration feature for KEEPER.

This package provides the web UI and data model for users to start
a move of their KEEPER account from an old email identity to a new one.

The actual heavy migration logic remains on the automation host
and is driven by periodic polling of this table.
"""
default_app_config = 'keeper.migration.apps.MigrationConfig'