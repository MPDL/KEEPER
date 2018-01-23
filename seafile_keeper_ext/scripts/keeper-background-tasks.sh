#!/bin/bash

echo ""

SCRIPT=$(readlink -f "$0")
INSTALLPATH="$(dirname $(dirname "${SCRIPT}"))/seafile-server-latest"
TOPDIR=$(dirname "${INSTALLPATH}")
default_ccnet_conf_dir=${TOPDIR}/ccnet

logdir=${TOPDIR}/logs
pro_pylibs_dir=${INSTALLPATH}/pro/python

seafevents_conf=${TOPDIR}/conf/seafevents.conf
seafile_background_tasks_log=${logdir}/seafile-background-tasks.log

seahub_dir=${INSTALLPATH}/seahub
central_config_dir=${TOPDIR}/conf

export SEAHUB_DIR=${seahub_dir}
export PATH=${INSTALLPATH}/seafile/bin:$PATH
export SEAFILE_LD_LIBRARY_PATH=${INSTALLPATH}/seafile/lib/:${INSTALLPATH}/seafile/lib64:${LD_LIBRARY_PATH}

script_name=$0
function usage () {
    echo "Usage: "
    echo
    echo "  $(basename "${script_name}") { start <port> | stop | restart <port> }"
    echo
    echo ""
}

# Check args
if [[ $1 != "start" && $1 != "stop" && $1 != "restart" ]]; then
    usage;
    exit 1;
fi

function check_python_executable() {
    if [[ "$PYTHON" != "" && -x $PYTHON ]]; then
        return 0
    fi

    if which python2.7 2>/dev/null 1>&2; then
        PYTHON=python2.7
    elif which python27 2>/dev/null 1>&2; then
        PYTHON=python27
    elif which python2.6 2>/dev/null 1>&2; then
        PYTHON=python2.6
    elif which python26 2>/dev/null 1>&2; then
        PYTHON=python26
    else
        echo
        echo "Can't find a python executable of version 2.6 or above in PATH"
        echo "Install python 2.6+ before continue."
        echo "Or if you installed it in a non-standard PATH, set the PYTHON enviroment varirable to it"
        echo
        exit 1
    fi
}

function validate_ccnet_conf_dir () {
    if [[ ! -d ${default_ccnet_conf_dir} ]]; then
        echo "Error: there is no ccnet config directory."
        echo "Have you run setup-seafile.sh before this?"
        echo ""
        exit -1;
    fi
}

function read_seafile_data_dir () {
    seafile_ini=${default_ccnet_conf_dir}/seafile.ini
    if [[ ! -f ${seafile_ini} ]]; then
        echo "${seafile_ini} not found. Now quit"
        exit 1
    fi
    seafile_data_dir=$(cat "${seafile_ini}")
    if [[ ! -d ${seafile_data_dir} ]]; then
        echo "Your seafile server data directory \"${seafile_data_dir}\" is invalid or doesn't exits."
        echo "Please check it first, or create this directory yourself."
        echo ""
        exit 1;
    fi

    pidfile=${TOPDIR}/pids/seafile-background-tasks.pid
}

function ensure_single_instance () {
    if pgrep -f "seafevents.background_tasks" 2>/dev/null 1>&2; then
        echo "seafile background tasks is already running."
        exit 1;
    fi
}

function warning_if_seafile_not_running () {
    if ! pgrep -f "seafile-controller -c ${default_ccnet_conf_dir}" 2>/dev/null 1>&2; then
        echo
        echo "Warning: seafile-controller not running. Have you run \"./seafile.sh start\" ?"
        echo
    fi
}

function prepare_log_dir() {
    if ! [[ -d ${logsdir} ]]; then
        if ! mkdir -p "${logdir}"; then
            echo "ERROR: failed to create logs dir \"${logdir}\""
            exit 1
        fi
    fi
}

function before_start() {
    warning_if_seafile_not_running;
    ensure_single_instance;
    prepare_log_dir;

    export CCNET_CONF_DIR=${default_ccnet_conf_dir}
    export SEAFILE_CONF_DIR=${seafile_data_dir}
    export SEAFILE_CENTRAL_CONF_DIR=${central_config_dir}
    export PYTHONPATH=${INSTALLPATH}/seafile/lib/python2.6/site-packages:${INSTALLPATH}/seafile/lib64/python2.6/site-packages:${INSTALLPATH}/seahub/thirdpart:$PYTHONPATH
    export PYTHONPATH=${INSTALLPATH}/seafile/lib/python2.7/site-packages:${INSTALLPATH}/seafile/lib64/python2.7/site-packages:$PYTHONPATH
    export PYTHONPATH=$PYTHONPATH:$pro_pylibs_dir
    export PYTHONPATH=$PYTHONPATH:${INSTALLPATH}/seahub-extra/
    export PYTHONPATH=$PYTHONPATH:${INSTALLPATH}/seahub-extra/thirdparts
    # Allow LDAP user sync to import seahub_settings.py
    export PYTHONPATH=$PYTHONPATH:${central_config_dir}
    # KEEPER: added due to keeper deps
    export PYTHONPATH=$PYTHONPATH:$SEAHUB_DIR
    export SEAFES_DIR=$pro_pylibs_dir/seafes
}

function start_seafile_background_tasks () {
    before_start;
    echo "Starting seafile background tasks ..."
    $PYTHON -m seafevents.background_tasks --config-file "${seafevents_conf}" \
        --loglevel debug --logfile "${seafile_background_tasks_log}" -P "${pidfile}" 2>/dev/null 1>&2 &

    # Ensure started successfully
    sleep 5
    if ! pgrep -f "seafevents.background_tasks" >/dev/null; then
        printf "\033[33mError: failed to start seafile background tasks.\033[m\n"
        echo "Please try to run \"./seafile-background-tasks.sh start\" again"
        exit 1;
    fi
}

function stop_seafile_background_tasks () {
    if [[ -f ${pidfile} ]]; then
        pid=$(cat "${pidfile}")
        echo "Stopping seafile background tasks ..."
        kill "${pid}"
        sleep 1
        if ps "${pid}" 2>/dev/null 1>&2 ; then
            kill -KILL "${pid}"
        fi
        pkill -f "soffice.*--invisible --nocrashreport"
        rm -f "${pidfile}"
        return 0
    else
        echo "seafile background tasks is not running"
    fi
}

check_python_executable;
validate_ccnet_conf_dir;
read_seafile_data_dir;

case $1 in
    "start" )
        start_seafile_background_tasks;
        ;;
    "stop" )
        stop_seafile_background_tasks;
        ;;
    "restart" )
        stop_seafile_background_tasks
        sleep 2
        start_seafile_background_tasks
        ;;
esac

echo "Done."
echo ""
