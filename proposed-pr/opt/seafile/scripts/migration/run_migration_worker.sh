#!/bin/bash
# Simple wrapper to run the self-service migration worker.
# Deploy this to /opt/seafile/scripts/migration/ along with the .py files.
# Usage: ./run_migration_worker.sh [--dry-run] [--list-pending]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load env if present (for DB creds, etc.)
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

python3 process_keeper_email_migrations.py "$@"
