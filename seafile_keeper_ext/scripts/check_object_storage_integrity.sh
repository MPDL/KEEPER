#!/bin/bash
#set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest


RC=0

PID_FILE="${SEAFILE_LATEST_DIR}/runtime/object_storage_integrity.$$.pid"
#remove PID on EXIT
trap "rm -f -- '$PID_FILE'" EXIT


# INJECT ENV
source "${SEAFILE_DIR}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

exec > >(tee __KEEPER_LOG_DIR__/keeper_object_sorage_integrity.`date '+%Y-%m-%d'`.log)
exec 2>&1 


# check seafile object storage integrity
function check_object_storage_integrity () {
    pushd $SEAFILE_LATEST_DIR
    RESULT="$(sudo -u seafile ./seaf-fsck.sh)"
    echo "${RESULT}"
    if [[ "$RESULT" =~ "is corrupted" ]]; then
        RC=1
        warn "Object Storage integrity test has failed"
    fi
    popd
}


###### CHECK 

# check_object_storage_integrity.sh is already running!
if [  $(find "${SEAFILE_LATEST_DIR}/runtime" -name "object_storage_integrity.*.pid" )  ]; then
    err_and_exit "$(basename $0) is already running, please check!"
fi

if [ ! -L "${SEAFILE_LATEST_DIR}" ]; then
	err_and_exit "Link $SEAFILE_LATEST_DIR does not exist."
fi

#TODO: check GPFS mount, probably more precise method! 
RESULT=$(mount -t gpfs)
if [[ ! "$RESULT" =~ "${__GPFS_DEVICE__} on /keeper type gpfs" ]]; then
	err_and_exit "Cannot find mounted gpfs: $RESULT" 
fi

#create PID file
echo $$ > "$PID_FILE"

##### START
echo "seaf_fsck started at $(date)"
START=$(timestamp)

#sleep 5
check_object_storage_integrity

echo "seaf_fsck ended at $(date)"
echo_green "Elapsed time: $(elapsed_time ${START})\n"

[ $RC -ne 0  ] && err_and_exit "seaf_fsck found Object Storage inconsistencies"

echo_green "seaf_fsck is successful!"
exit 0


