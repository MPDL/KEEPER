#!/bin/bash
#
# deploy-migration.sh
#
# Deploy *only* the self-service email migration components for KEEPER.
# Designed to run on top of an already deployed KEEPER instance.
#
# Role-aware (based on __NODE_TYPE__ from keeper*.ini or env):
#   - BACKGROUND (or the BG server): deploys the worker scripts to /opt/seafile/scripts/migration/
#     (process_keeper_email_migrations.py, the legacy migrate_account.py + seafile_common.py, etc.)
#   - APP (or the application server): deploys the frontend/UI bits:
#     - seahub-data/custom/templates/keeper/migration/ + keeper-migration.css
#     - the Python package seafile-server-latest/seahub/keeper/migration/ (so /account/migrate/ works)
#   - SINGLE: deploys both.
#
# This is a targeted deploy script. It is inspired by the deploy-dir / deploy_file logic
# in keeper_setup.sh and build.py.
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

# Always announce on exit (for diagnosing silent/early exits under set -e during detection on real servers)
trap 'rc=$?; echo "=== deploy-migration.sh EXIT trap (rc=$rc, mode=$MODE, node=${NODE_TYPE:-unset}) ===" >&2' EXIT

echo "=== deploy-migration.sh starting (mode=$MODE, EXT_DIR=$EXT_DIR) ==="

# -----------------------------
# Role detection (APP / BACKGROUND / SINGLE) based on __NODE_TYPE__
# This makes the targeted migration deploy do the right thing per server role.
# BACKGROUND -> worker scripts + cron
# APP        -> UI (custom templates/css + the keeper/migration Python package for the frontend)
# SINGLE     -> both
#
# Detection uses ONLY safe grep/sed parse of /opt/seafile/keeper*.ini (get_keeper_ini_value helper).
# We never rely on sourcing inject_keeper_env.sh for NODE_TYPE (it can do explicit exit 1, killing
# the shell even under set +e / subshell / || true, as seen when "sourcing..." printed then rc=1 trap).
# The keeper*.ini is ALWAYS directly under /opt/seafile (e.g. keeper-app07-qa.ini).
# We probe ONLY /opt/seafile/keeper*.ini and do not expand the search.
# -----------------------------

# Safe parser: ONLY reads /opt/seafile/keeper*.ini using grep/sed.
# NEVER sources inject_keeper_env.sh here (it can contain explicit "exit 1" which would kill the shell
# even inside set +e or subshells, as seen in the crash where sourcing printed then rc=1).
get_keeper_ini_value() {
  local key="$1"
  local line="" val=""
  shopt -s nullglob 2>/dev/null || true
  for ini in /opt/seafile/keeper*.ini ; do
    if [ -f "$ini" ]; then
      # loose match (no ^) so it finds keys even under [global] or other sections
      line=$(grep -i "${key}[[:space:]]*=" "$ini" 2>/dev/null | head -1 || true)
      if [ -n "$line" ]; then
        # Take EVERYTHING after the FIRST '=' verbatim; trim only surrounding
        # whitespace and CR. Do NOT strip '#', '=', or inner spaces — values
        # such as __DB_PASSWORD__ may legitimately contain them.
        val=$(printf '%s' "$line" | tr -d '\r' \
          | sed -e 's/^[^=]*=//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        [ -n "$val" ] && break
      fi
    fi
  done
  shopt -u nullglob 2>/dev/null || true
  printf %s "$val"
}

echo ">>> NODE_TYPE detection starting (safe parser only, no inject source) ..."

# The keeper*.ini is ALWAYS located directly under /opt/seafile (e.g. /opt/seafile/keeper-app07-qa.ini).
# Do NOT expand the search to KEEPER/, conf/, parent dirs, or anywhere else.
echo ">>> Direct keeper*.ini probe under /opt/seafile (ALWAYS the location) ..."
shopt -s nullglob 2>/dev/null || true
for ini in /opt/seafile/keeper*.ini ; do
  if [ -f "$ini" ]; then
    echo "      direct ini found: $ini"
    raw=$(grep -i '__NODE_TYPE__' "$ini" 2>/dev/null | head -1 || true)
    echo "      raw line from ini: $raw"
    if [ -z "$NODE_TYPE" ]; then
      # Robust extraction
      val=$(echo "$raw" | sed -e 's/.*= *//' -e 's/[[:space:]#].*//' -e 's/ //g' -e 's/\r//g' | tr '[:lower:]' '[:upper:]' || true)
      if [ -n "$val" ]; then
        echo "      extracted NODE_TYPE='$val' from /opt/seafile/keeper*.ini"
        NODE_TYPE="$val"
      fi
    fi
  fi
done
shopt -u nullglob 2>/dev/null || true

# Optional isolated attempt to get NODE_TYPE from inject (in separate bash -c so any exit 1 inside
# only kills the child, never reaches our main shell or trap with rc=1).
if [ -z "$NODE_TYPE" ] && [ -f "${EXT_DIR}/scripts/inject_keeper_env.sh" ]; then
  echo "    attempting isolated bash -c source of inject for NODE_TYPE (safe) ..." >&2
  ISOLATED=$(bash -c '
    set +e
    source "'"${EXT_DIR}/scripts/inject_keeper_env.sh"'" >/dev/null 2>&1 || true
    printf %s "${__NODE_TYPE__:-}"
  ' 2>/dev/null || true)
  if [ -n "$ISOLATED" ]; then
    NODE_TYPE="$ISOLATED"
    echo "      got NODE_TYPE from isolated inject"
  fi
fi

if [ -z "$NODE_TYPE" ]; then
  echo ">>> Still no NODE_TYPE after /opt/seafile probe; minimal fallback scan (restricted to /opt/seafile ONLY) ..."
  for d in /opt/seafile ; do
    echo "    scanning d=$d (ALWAYS /opt/seafile only - no expansion)"
    shopt -s nullglob 2>/dev/null || true
    for ini in "$d"/keeper*.ini ; do
      if [ -f "$ini" ]; then
        echo "      candidate ini=$ini"
        raw=$(grep -i '__NODE_TYPE__' "$ini" 2>/dev/null | head -1 || true)
        echo "      raw line from ini: $raw"
        val=$(echo "$raw" | sed -e 's/.*= *//' -e 's/[[:space:]#].*//' -e 's/ //g' -e 's/\r//g' | tr '[:lower:]' '[:upper:]' || true)
        if [ -n "$val" ]; then
          NODE_TYPE="$val"
          break 2
        fi
      fi
    done
    shopt -u nullglob 2>/dev/null || true
  done
fi

# Do NOT silently default the role: an undetected NODE_TYPE would skip the
# worker (on a BACKGROUND node) or the UI (on an APP node) while still
# reporting a successful deploy. Fail loudly and let the operator be explicit.
if [ -z "$NODE_TYPE" ]; then
    echo "" >&2
    echo "ERROR: could not detect __NODE_TYPE__ from /opt/seafile/keeper*.ini." >&2
    echo "       Re-run with the role set explicitly, e.g.:" >&2
    echo "           NODE_TYPE=BACKGROUND $0 standalone" >&2
    echo "       Valid values: APP | BACKGROUND | SINGLE" >&2
    exit 1
fi

NODE_TYPE="$(echo "$NODE_TYPE" | tr '[:lower:]' '[:upper:]')"
case "$NODE_TYPE" in
    APP|BACKGROUND|SINGLE) ;;
    *)
        echo "ERROR: unknown NODE_TYPE='$NODE_TYPE' (valid: APP | BACKGROUND | SINGLE)." >&2
        exit 1
        ;;
esac

is_background=false
case "$NODE_TYPE" in
    BACKGROUND) is_background=true ;;
esac

echo "Detected NODE_TYPE=$NODE_TYPE (is_background=$is_background)"

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
# Main deploy steps (role-aware)
# -----------------------------

echo "=== KEEPER self-service email migration targeted deploy ==="
echo "Mode: $MODE"
echo "Source ext dir: $EXT_DIR"
echo "Target SEAFILE_DIR: $SEAFILE_DIR"
echo "NODE_TYPE: $NODE_TYPE (is_background=$is_background)"
echo ""

# Scripts (the worker + legacy migrate tools) belong on BACKGROUND servers
if $is_background || [ "$NODE_TYPE" = "SINGLE" ]; then
    echo ">>> Deploying scripts/migration (for BACKGROUND node - the migration worker) ..."
    mkdir -p "$MIGRATION_DEST_DIR"
    deploy_dir_targeted "$MIGRATION_SRC_DIR" "$MIGRATION_DEST_DIR"

    # Make shell wrappers executable in dest (idempotent)
    if [ -f "${MIGRATION_DEST_DIR}/run_migration_worker.sh" ]; then
        chmod +x "${MIGRATION_DEST_DIR}/run_migration_worker.sh" || true
    fi
    echo ">>> scripts/migration deployment complete."

    # Deploy the cron job for the migration worker (same mechanism as other system/cron.d.* files)
    CRON_SRC="${EXT_DIR}/system/cron.d.keeper-migration"
    CRON_DEST="/etc/cron.d/cron-keeper-migration"
    if [ -f "$CRON_SRC" ]; then
        echo ">>> Deploying cron.d for migration worker (BACKGROUND) ..."
        # NO backup inside /etc/cron.d: cron treats ANY file matching
        # [A-Za-z0-9_-]+ there as a live crontab, so a *_orig copy would be
        # scheduled too (double runs). This matches build.py, which deploys all
        # cron.d.* files with skip_backup=True — the file is regenerated
        # deterministically from the source anyway.
        # Also remove a stale backup left by earlier versions of this script:
        rm -f "${CRON_DEST}${BACKUP_POSTFIX}"
        # Expand using known vars (mimics the expand_properties in main deploy)
        if [ -n "$SEAFILE_DIR" ]; then
            sed -e "s#__SEAFILE_DIR__#${SEAFILE_DIR}#g" \
                -e "s#__OS_USER__#${__OS_USER__:-seafile}#g" \
                "$CRON_SRC" > "$CRON_DEST"
            echo "    expanded and deployed to $CRON_DEST"
        else
            cp -a "$CRON_SRC" "$CRON_DEST"
            echo "    copied raw to $CRON_DEST"
        fi
        chmod 644 "$CRON_DEST" || true
    fi

    # ------------------------------------------------------------------
    # Integrate next steps: execute pip + sql table (instead of only printing notes)
    # These are now performed here (for both standalone and slipstream modes)
    # so that after ./deploy-migration.sh the worker is closer to ready.
    # pip is made robust for re-runs and modern pip ("without issues always").
    # sql uses the idempotent create_ script (CREATE IF NOT EXISTS + safe ALTER).
    # ------------------------------------------------------------------
    echo ">>> Integrating next steps (pip install + idempotent DB table) ..."

    # pip: always safe to re-run; handle --break-system-packages for newer pip,
    # reduce noise, never abort the deploy on pip hiccups.
    if [ -f "${MIGRATION_DEST_DIR}/requirements.txt" ]; then
        echo "    pip3 install -r requirements.txt (robust, re-runnable) ..."
        PIP_OPTS="--disable-pip-version-check --quiet --no-warn-script-location"
        if pip3 install --help 2>&1 | grep -q -- '--break-system-packages'; then
            PIP_OPTS="$PIP_OPTS --break-system-packages"
        fi
        ( cd "$MIGRATION_DEST_DIR" && pip3 install -r requirements.txt $PIP_OPTS 2>&1 ) || true
        echo "    pip step completed."
    fi

    # SQL table: auto-apply the idempotent DDL. Use the provided DB vars from keeper*.ini
    # (__DB_HOST__, __DB_USER__, __DB_PORT__, __DB_PASSWORD__). DB name is always keeper-db.
    # No manual steps are ever printed; if creds missing we just skip silently (table may already exist).
    SQLF="${MIGRATION_DEST_DIR}/create_keeper_email_migration_table.sql"
    if [ -f "$SQLF" ] && command -v mysql >/dev/null 2>&1; then
        echo "    applying idempotent SQL (create table if not exists) ..."
        # load .env if the operator placed one before running deploy (standard .env, low risk of exit)
        if [ -f "${MIGRATION_DEST_DIR}/.env" ]; then
            set +e
            . "${MIGRATION_DEST_DIR}/.env" >/dev/null 2>&1 || true
            set -e
        fi
        # Safe parse from the ini ONLY (using the exact vars you provided; no source of inject)
        __DB_HOST__=$(get_keeper_ini_value '__DB_HOST__')
        __DB_PORT__=$(get_keeper_ini_value '__DB_PORT__')
        __DB_USER__=$(get_keeper_ini_value '__DB_USER__')
        __DB_PASSWORD__=$(get_keeper_ini_value '__DB_PASSWORD__')
        H=${KEEPER_DB_HOST:-${DB_HOST:-${__DB_HOST__:-localhost}}}
        P=${KEEPER_DB_PORT:-${DB_PORT:-${__DB_PORT__:-3306}}}
        D=keeper-db
        U=${KEEPER_DB_USER:-${DB_USER:-${__DB_USER__:-}}}
        PW=${KEEPER_DB_PASSWORD:-${DB_PASSWORD:-${__DB_PASSWORD__:-}}}
        if [ -n "$U" ]; then
            # Password via MYSQL_PWD (never on the command line): keeps it out of
            # `ps`/process lists and immune to shell word-splitting on special chars.
            # Check the exit code — a silently failed apply would leave the worker
            # without its table while the deploy still reports success.
            set +e
            MYSQL_PWD="$PW" mysql -h "$H" -P "$P" -u "$U" "$D" < "$SQLF"
            SQL_RC=$?
            set -e
            if [ "$SQL_RC" -eq 0 ]; then
                echo "    SQL table ensured (idempotent)."
            else
                echo "    WARNING: could not apply $SQLF (mysql exit $SQL_RC)." >&2
                echo "             Check DB credentials (__DB_*__ in /opt/seafile/keeper*.ini or .env)," >&2
                echo "             then apply manually: mysql -h $H -P $P -u $U -p keeper-db < $SQLF" >&2
            fi
        else
            echo "    (no DB creds from ini/.env; skipping auto-apply, table may already exist from previous run)"
        fi
    else
        echo "    (mysql client or $SQLF not present for auto table apply)"
    fi

    echo ">>> Integrated next steps complete (pip + table)."
else
    echo ">>> Skipping scripts/migration (this is an APP node; scripts go to the BACKGROUND server)"
fi

echo ""

# UI (templates/css) + the keeper/migration Python package belong on APP servers (the frontend)
if ! $is_background || [ "$NODE_TYPE" = "SINGLE" ]; then
    echo ">>> Deploying seahub-data/custom for migration UI (for APP node) ..."

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

    # Deploy the Python package for the migration UI so the views/urls are live on APP
    # (keeper/migration/ under the installed seahub).
    #
    # IDEMPOTENT: take a one-time backup, then always mirror SRC -> DEST exactly.
    # We remove the live copy *first* so repeated runs never nest the source inside
    # the destination (the old `cp -a SRC DEST` into an existing DEST created
    # DEST/migration/ and left the real views.py stale).
    KEEPER_MIGRATION_SRC="${EXT_DIR}/seafile-server-latest/seahub/keeper/migration"
    KEEPER_MIGRATION_DEST="${SEAFILE_LATEST_DIR}/seahub/keeper/migration"
    if [ -d "$KEEPER_MIGRATION_SRC" ]; then
        echo ">>> Deploying keeper/migration Python package (for APP/frontend) ..."
        mkdir -p "$(dirname "$KEEPER_MIGRATION_DEST")"
        if [ -d "$KEEPER_MIGRATION_DEST" ]; then
            BACKUP="${KEEPER_MIGRATION_DEST}${BACKUP_POSTFIX}"
            if [ ! -d "$BACKUP" ]; then
                echo "Backing up existing $KEEPER_MIGRATION_DEST -> $BACKUP (one-time)"
                cp -a "$KEEPER_MIGRATION_DEST" "$BACKUP" || true
            else
                echo "Backup already exists: $BACKUP, keeping it"
            fi
            # Remove the current live copy so the fresh copy fully replaces it
            # (prevents cp -a from nesting SRC inside DEST on repeated runs).
            rm -rf "$KEEPER_MIGRATION_DEST"
        fi
        cp -a "$KEEPER_MIGRATION_SRC" "$KEEPER_MIGRATION_DEST"
        # Drop stale bytecode so the freshly copied .py files are what load after a seahub restart.
        find "$KEEPER_MIGRATION_DEST" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
        find "$KEEPER_MIGRATION_DEST" -type f -name '*.pyc' -delete 2>/dev/null || true
        echo "    keeper/migration Python package deployed (idempotent mirror, bytecode cleared)."
        echo "    NOTE: restart seahub to load updated Python (templates/CSS need no restart)."
    fi
else
    echo ">>> Skipping seahub-data/custom + keeper/migration Python (this is a BACKGROUND node)"
fi

echo ""

# Post-deploy notes (tailored a bit by role)
echo "=== Post-deploy notes (migration only) ==="
if $is_background || [ "$NODE_TYPE" = "SINGLE" ]; then
    echo "- Scripts are now in: $MIGRATION_DEST_DIR"
    echo "  (pip install + idempotent table creation were executed automatically above)"
    echo "  (configure .env with KEEPER_DB_* creds + SMTP if notifications wanted; cron is auto-installed)"
fi
if ! $is_background || [ "$NODE_TYPE" = "SINGLE" ]; then
    echo "- Custom templates/CSS are in: $CUSTOM_DEST_DIR"
    echo "  (UI should be live immediately via the seahub-data/custom symlink on APP)"
    echo "- keeper/migration Python package is in the installed seahub (APP)"
    echo "- IMPORTANT: restart seahub so updated Python (views.py/urls.py) is loaded:"
    echo "      keeper-service stop && sleep 10 && keeper-service start"
fi
echo ""
if [ "$MODE" = "standalone" ]; then
    echo "Remaining manual steps (standalone mode or first time):"
    if $is_background || [ "$NODE_TYPE" = "SINGLE" ]; then
        echo "  # .env: keeper-db + SMTP + MySQL creds + SEAFILE_SERVER_URL are auto-imported"
        echo "  #   from /opt/seafile/keeper-*.ini; privileged steps run locally (no SSH)."
        echo "  #   The only value you normally must set is SEAFILE_AUTH_TOKEN (admin API token):"
        echo "  #   cp .env.example .env ; edit .env   # set SEAFILE_AUTH_TOKEN"
        echo "  # Test the worker:"
        echo "  cd $MIGRATION_DEST_DIR"
        echo "  ./run_migration_worker.sh --dry-run --list-pending"
        echo ""
        echo "  # Cron for the worker was automatically deployed + expanded to /etc/cron.d/cron-keeper-migration"
        echo "  # (runs every 5 min; no manual crontab edit needed)"
    fi
    # Note: web UI bits and table creation have no manual steps listed (auto-deployed / auto-applied where possible).
    echo ""
fi
echo "=== deploy-migration.sh finished (mode=$MODE, node=$NODE_TYPE) ==="
