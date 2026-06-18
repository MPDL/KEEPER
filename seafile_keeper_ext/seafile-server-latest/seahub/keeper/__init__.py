"""
KEEPER extension package.

Includes self-service email migration feature:
- Web UI at /account/migrate/ (source gets code, target pastes after checking the account banner).
- Model in migration/models.py (table in keeper-db).
- Admin and management command for monitoring.
- URLs ready to include.

Ops scripts (worker, etc.) are in /opt/seafile/scripts/migration/ (deployed via scripts/ dir).
"""
