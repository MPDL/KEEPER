#!/bin/bash

SCRIPT=$(readlink -f $0)
CURR_DIR=$(dirname $SCRIPT)
source "${CURR_DIR}/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
    echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

ATTEMPTS=5
DELAY=5

function check_seafile_background_tasks () {
    if ! pgrep -f "seafevents.background_tasks" >/dev/null; then
        echo "DEAD"; 
    else
        echo "OK";
    fi
}

function do_check_and_start () {

    i=1
    while [ $i -le "$ATTEMPTS" ]; do
        result=$(check_seafile_background_tasks)
        if [ $result == "DEAD" ]; then
            echo "background_tasks are dead, trying to start, attempt ${i}..."
            ${CURR_DIR}/keeper-background-tasks.sh start
        else
            break
        fi
        i=$(($i+1))
        sleep $DELAY
    done
    if [ $i -eq $(($ATTEMPTS+1)) ]; then
        err_and_exit "cannot start background_tasks process"
    elif [ $i -eq 1 ]; then
        echo_green "background_tasks are already running, nothing to start..."
    else
        echo_green "background_tasks have been succesfully started"
    fi

}
echo ""
echo "./$(basename $0) started at $(date)"
do_check_and_start

