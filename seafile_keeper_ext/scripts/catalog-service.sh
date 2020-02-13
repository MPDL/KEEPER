#!/bin/bash

#set -x

CURR_DIR=$(dirname $(readlink -f $0))
source "${CURR_DIR}/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi
GATALOG_PID_FILE=${SEAFILE_LATEST_DIR}/runtime/catalog.pid


function start_catalog () {
    export PYTHON_EGG_CACHE=$(echo ~${__OS_USER__})/.cache/Python-Eggs
    uwsgi --pidfile $GATALOG_PID_FILE --ini ${SEAFILE_LATEST_DIR}/seahub/keeper/catalog/catalog.ini 2>/dev/null & 
    sleep 2
    if [ ! -f "$GATALOG_PID_FILE" ]; then
        echo "Cannot find PID file, catalog is not started"
        exit 1 
    fi 
    if ! ps -p $(cat $GATALOG_PID_FILE) > /dev/null; then
        echo "Cannot find PID process, catalog is not started"
        exit 1 
    fi    
}

function clean_pid_file () {
    rm $CATALOG_PID_FILE 2>/dev/null
}

function stop_catalog () {
    if ! pgrep -f "uwsgi.*catalog.ini" >/dev/null; then
        clean_pid_file
        exit 0        
    fi
    if [ ! -f "$GATALOG_PID_FILE" ]; then
        echo "Cannot find PID file, killing..."
        pkill -f "uwsgi.*catalog.ini" -9
        exit $RC
    fi
    PID=$(cat $GATALOG_PID_FILE) 
    if ! ps -p $PID > /dev/null; then
        echo "Cannot find PID process, wrong PID file? Clean it and killing..."
        clean_pid_file
        pkill -f "uwsgi.*catalog.ini" -9
        exit 0
    fi
    uwsgi --stop $GATALOG_PID_FILE 
    sleep 2
    if [ $(ps -p $PID > /dev/null) ] || [ -f "$CATALOG_PID_FILE" ]; then
        echo "Catalog is still running, clean and kill..."
        clean_pid_file
        pkill -f "uwsgi.*catalog.ini" -9
        exit 0
    fi

}

function run_catalog_manager() {
    RESULT=$($SEAFILE_DIR/scripts/run_keeper_script.sh $SEAFILE_LATEST_DIR/seahub/keeper/catalog/catalog_manager.py $1)    
    echo $RESULT
}

if [[ -n $VIRTUAL_ENV ]]; then
    export PYTHONPATH=${VIRTUAL_ENV}/lib/python2.7/site-packages:$PYTHONPATH
    export PATH=${VIRTUAL_ENV}/bin:$PATH
fi


case "$1" in
        start|restart)
            if [ "$1" = "restart" ]; then
                stop_catalog
            fi
            start_catalog
        ;;
        stop)
            stop_catalog
        ;;
        clean-db|gen-db)
            run_catalog_manager $1
        ;;
        sync-db)
            echo $0
            $0 clean-db
            $0 gen-db
        ;;
        *)
            echo "Usage: $0 {start|stop|restart|clean-db|gen-db|sync-db}"
            exit 1
        ;;
esac


