#!/bin/bash

#set -x

SEAFILE_DIR=/opt/seafile/seafile-server-latest
GATALOG_PID_FILE=${SEAFILE_DIR}/runtime/catalog.pid

function start_catalog () {
    uwsgi --pidfile $GATALOG_PID_FILE --ini ${SEAFILE_DIR}/seahub/keeper/catalog/catalog.ini 2>/dev/null & 
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
    RESULT=$($SEAFILE_DIR/../scripts/run_keeper_script.sh $SEAFILE_DIR/seahub/keeper/catalog/catalog_manager.py $1)    
    echo $RESULT
}

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


