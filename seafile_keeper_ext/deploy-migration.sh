#!/bin/bash
#
# deploy-migration.sh
#
# Deploy *only* the self-service email migration components for KEEPER.
# Designed to run on top of an already deployed KEEPER instance.
#
# This is a targeted deploy script (scripts/migration/ + seahub-data/custom/ bits for the UI).
# It is inspired by the deploy-dir / deploy_file logic in keeper_setup.sh and build.py.
#
# The single parameter defines the deployment context:
#   slipstream | build   - Called from build.py (or keeper_setup during full redeploy).
#                           Non-interactive, no questions, always backup+overwrite.
#   standalone          - Run manually by ops on an existing deployed system to
#                           update/overlay just the migration pieces (with prompts).
#
# Usage:
#   cd /path/to/seafile_keeper_ext
#   ./deploy-migration.sh standalone
#   ./deploy-migration.sh slipstream
#
# After deploy (standalone):
#   - Review /opt/seafile/scripts/migration/.env and requirements.txt
#   - pip3 install -r requirements.txt   (in the dest dir, if changed)
#   - The create_keeper_email_migration_table.sql is included (run manually if needed)
#   - Custom templates/CSS are in seahub-data/custom/ (usually live immediately via symlink)
#   - Restart seahub if Python package parts under seahub/keeper/migration were also updated
#     (this script does not touch the Python package; use full deploy or copy for that)
#
# Connection to build.py:
#   python build.py deploy --migration     (or --ext which already covers scripts/seahub-data)
#   build.py invokes this script with the "slipstream" parameter for the targeted bits.
#
# See also:
#   keeper_setup.sh deploy-dir scripts/migration
#   keeper_setup.sh deploy-dir seahub-data/custom   (or the full deploy-all)
#

set -e

EXT_DIR=$(dirname "$(readlink -f "$0")")
SEAFILE_DIR=${SEAFILE_DIR:-/opt/seafile}
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest

# Migration sources (relative to this ext checkout)
MIGRATION_SRC_DIR="${EXT_DIR}/scripts/migration"
CUSTOM_SRC_DIR="${EXT_DIR}/seahub-data/custom"

# Destinations on the live instance
MIGRATION_DEST_DIR="${SEAFILE_DIR}/scripts/migration"
CUSTOM_DEST_DIR="${SEAFILE_DIR}/seahub-data/custom"

BACKUP_POSTFIX="_orig"

MODE="${1:-standalone}"

if [ "$MODE" = "build" ]; then
    MODE="slipstream"
fi

if [[ "$MODE" != "slipstream" && "$MODE" != "standalone" ]]; then
    echo "Usage: $0 {slipstream|standalone|build}"
    echo ""
    echo "  slipstream | build   Slipstreamed / invoked via build.py deploy --migration"
    echo "                       (non-interactive, for use inside full KEEPER deploy flows)"
    echo ""
    echo "  standalone           Manual targeted deploy on an already-deployed KEEPER"
    echo "                       instance (prompts before overwriting files)"
    echo ""
    exit 1
fi

# -----------------------------
# Helper functions (adapted from keeper_setup.sh for self-contained operation)
# -----------------------------

err_and_exit() {
    echo "ERROR: $1" >&2
    exit 1
}

check_file() {
    if [ ! -f "$1" ]; then
        err_and_exit "File does not exist: $1"
    fi
}

check_dir() {
    if [ ! -d "$1" ]; then
        err_and_exit "Directory does not exist: $1"
    fi
}

create_dir_for_file() {
    local DEST_DIR
    DEST_DIR=$(dirname "$1")
    if [ ! -d "$DEST_DIR" ]; then
        echo "Creating directory: $DEST_DIR"
        mkdir -p "$DEST_DIR" || err_and_exit "Cannot create dir $DEST_DIR"
    fi
}

backup_file() {
    # $1 = file to backup
    check_file "$1"
    local BACKUP_FILE="${1}${BACKUP_POSTFIX}"
    if [ -f "$BACKUP_FILE" ]; then
        echo "Backup already exists: $BACKUP_FILE, skipping!"
    else
        echo "Backing up $1 -> $BACKUP_FILE"
        mv -v "$1" "$BACKUP_FILE" || err_and_exit "Cannot backup $1"
    fi
}

# Deploy a single file with optional prompt (standalone) or forced (slipstream)
deploy_file_targeted() {
    local SRC="$1"
    local DEST="$2"

    check_file "$SRC"
    create_dir_for_file "$DEST"

    if [ -f "$DEST" ]; then
        if [ "$MODE" = "standalone" ]; then
            # Interactive prompt like keeper_setup.sh deploy
            read -r -p "Deploy file $SRC into $DEST (y/n)? " choice
            case "$choice" in
                y|Y ) echo "yes" ;;
                n|N ) echo "skipping $DEST"; return ;;
                * ) echo "invalid choice, skipping"; return ;;
            esac
        fi
        # In both modes, if file exists we backup before overwrite
        backup_file "$DEST"
    else
        if [ "$MODE" = "standalone" ]; then
            read -r -p "Deploy (new) file $SRC into $DEST (y/n)? " choice
            case "$choice" in
                y|Y ) echo "yes" ;;
                n|N ) echo "skipping $DEST"; return ;;
                * ) echo "invalid choice, skipping"; return ;;
            esac
        fi
    fi

    cp -av "$SRC" "$DEST" || err_and_exit "Cannot copy $SRC to $DEST"
}

# Deploy an entire directory tree (only files), preserving substructure.
# Used for scripts/migration (flat) and for custom sub-trees.
deploy_dir_targeted() {
    local SRC_BASE="$1"      # e.g. .../scripts/migration
    local DEST_BASE="$2"     # e.g. /opt/seafile/scripts/migration
    local REL_PREFIX="$3"    # optional, e.g. "templates/keeper/migration" when walking a subdir

    check_dir "$SRC_BASE"

    # Find files, exclude typical junk
    local SOURCE_FILES
    SOURCE_FILES=$(find -H "$SRC_BASE" -type f \
        ! -iname "*.pyc" \
        ! -path "*/.ropeproject/*" \
        ! -path "*/.cache/*" \
        ! -path "*/__pycache__/*" \
        ! -iname ".gitignore" \
        2>/dev/null || true)

    for f in $SOURCE_FILES; do
        # Compute relative path from SRC_BASE
        local rel
        rel="${f#$SRC_BASE/}"

        if [ -n "$REL_PREFIX" ]; then
            local dest
            dest="${DEST_BASE}/${REL_PREFIX}/${rel}"
        else
            local dest
            dest="${DEST_BASE}/${rel}"
        fi

        deploy_file_targeted "$f" "$dest"
    done
}

# -----------------------------
# Main deploy steps
# -----------------------------

echo "=== KEEPER self-service email migration targeted deploy ==="
echo "Mode: $MODE"
echo "Source ext dir: $EXT_DIR"
echo "Target SEAFILE_DIR: $SEAFILE_DIR"
echo ""

# 1. Operational scripts (worker, migrate_account.py, create sql, wrapper, requirements, README, .env.example-ish)
echo ">>> Deploying scripts/migration (ops worker + legacy scripts) ..."
mkdir -p "$MIGRATION_DEST_DIR"
deploy_dir_targeted "$MIGRATION_SRC_DIR" "$MIGRATION_DEST_DIR"

# Make shell wrappers executable in dest (idempotent)
if [ -f "${MIGRATION_DEST_DIR}/run_migration_worker.sh" ]; then
    chmod +x "${MIGRATION_DEST_DIR}/run_migration_worker.sh" || true
fi

echo ">>> scripts/migration deployment complete."
echo ""

# 2. UI custom bits (templates + css) that live under seahub-data/custom
echo ">>> Deploying seahub-data/custom for migration UI (templates + css) ..."

# keeper/migration templates
mkdir -p "${CUSTOM_DEST_DIR}/templates/keeper/migration"
deploy_dir_targeted "${CUSTOM_SRC_DIR}/templates/keeper/migration" "${CUSTOM_DEST_DIR}/templates/keeper" "migration"

# migration CSS
mkdir -p "${CUSTOM_DEST_DIR}/css"
if [ -f "${CUSTOM_SRC_DIR}/css/keeper-migration.css" ]; then
    deploy_file_targeted \
        "${CUSTOM_SRC_DIR}/css/keeper-migration.css" \
        "${CUSTOM_DEST_DIR}/css/keeper-migration.css"
fi

echo ">>> seahub-data/custom migration bits deployment complete."
echo ""

# 3. Post-deploy notes (always shown)
echo "=== Post-deploy notes (migration only) ==="
echo "- Scripts are now in: $MIGRATION_DEST_DIR"
echo "- Custom templates/CSS are in: $CUSTOM_DEST_DIR"
echo ""
echo "Next steps (standalone mode or first time):"
echo "  cd $MIGRATION_DEST_DIR"
echo "  pip3 install -r requirements.txt"
echo ""
echo "  # Ensure .env has your DB + (optionally) SMTP settings"
echo "  # Test: ./run_migration_worker.sh --dry-run --list-pending"
echo ""
echo "  # Typical cron (edit /etc/cron.d or crontab):"
echo "  # */5 * * * * cd $MIGRATION_DEST_DIR && python3 process_keeper_email_migrations.py >> /var/log/keeper-migration-worker.log 2>&1"
echo ""
echo "For the web UI (templates + CSS):"
echo "  - Usually live immediately (via seahub-data/custom symlink)."
echo "  - If using cached/compiled assets or after Python changes under keeper/migration/, restart seahub."
echo ""
echo "Table creation (if not already done):"
echo "  mysql ... keeper-db < $MIGRATION_DEST_DIR/create_keeper_email_migration_table.sql"
echo ""
echo "To also (re)deploy the Django app code (keeper/migration/*, keeper/urls.py etc):"
echo "  Use the normal full flow: keeper_setup.sh deploy-all   OR   python build.py deploy --ext"
echo "  (or manually rsync the seafile-server-latest/seahub/keeper/ tree)."
echo ""
echo "=== deploy-migration.sh finished (mode=$MODE) ==="
