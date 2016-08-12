#!/bin/bash
set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
BACKUP_POSTFIX="_orig"

PATH=$PATH:/usr/lpp/mmfs/bin
export PATH
TODAY=`date '+%Y%m%d'`
GPFS_DEVICE="/dev/gpfs_keeper"
GPFS_SNAPSHOT="mmbackupSnap${TODAY}"

# INJECT ENV
source "${SEAFILE_DIR}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

DB_BACKUP_DIR=/keeper/${__GPFS_FILESET__}/db-backup


function shutdown_seafile () {
    pushd ${SEAFILE_DIR}/scripts
    
    echo -e "Swicht keeper to maintenance mode...\n"
    ./seafile-server.sh switch-maintenance-mode
    if [ $? -ne 0  ]; then
        err_and_exit "Cannot switch keeper to maintenance mode"
    fi
    echo_green "OK"
    
    echo -e "Shutdown seafile...\n"
    ./seafile-server.sh stop
    if [ $? -ne 0  ]; then
        err_and_exit "Cannot stop seafile"
    fi
    echo_green "OK"
    
    popd
}

function startup_seafile () {
    pushd ${SEAFILE_DIR}/scripts

    echo -e "Startup seafile...\n"
    ./seafile-server.sh start
    if [ $? -ne 0  ]; then
        err_and_exit "Cannot start seafile"
    fi
    echo_green "OK"
    
    echo -e "Swicht keeper to normal mode...\n"
    ./seafile-server.sh switch-maintenance-mode
    if [ $? -ne 0  ]; then
        err_and_exit "Cannot switch keeper to normal mode"
    fi
    echo_green "OK"

    popd
}

# check seafile object storage integrity
function check_object_storage_integrity () {
    if [ $(date +'%u')  -eq "${__DAY_TO_CHECK_INTEGRITY__}" ]; then
        pushd $SEAFILE_LATEST_DIR
        ./seaf-fsck.sh
        if [ $? -ne 0  ]; then
            err_and_exit "Object storage integrity test has failed"
        fi
        popd
    fi
}

function backup_databases () {

    echo -e "Backup seafile databases...\n"

    # clean up old databases
    if [ "$(ls -A $DB_BACKUP_DIR)" ]; then
        echo "Clean ${DB_BACKUP_DIR}..."
        rm -v ${DB_BACKUP_DIR}/*
        [ $? -ne 0 ] && up_err_and_exit "Cannot clean up ${DB_BACKUP_DIR}"
    fi
    local TIMESTAMP=$(date +"%Y-%m-%d_%H:%M:%S")
    for i in ccnet seafile seahub keeper; do
        mysqldump -h${__DB_HOST__} -u${__DB_USER__} -p${__DB_PASSWORD__} --verbose ${i}-db | gzip > ${DB_BACKUP_DIR}/${TIMESTAMP}.${i}-db.sql.gz
        [ $? -ne 0  ] && up_err_and_exit "Cannot dump ${i}-db"
    done
    echo_green "Databases backup is OK"

}

function asynchronous_backup () {
	
    echo -e "Start asynchronous backup...\n"

	# 1. Backup GPFS-Config
    echo "Save GPFS backup config..."
    GPFS_BACKUP_CONF="/keeper/${__GPFS_FILESET__}/gpfs.config"
    # remove old one if exists
    [[ -e $GPFS_BACKUP_CONF ]] && rm -v $GPFS_BACKUP_CONF
    # save current
    mmbackupconfig $GPFS_DEVICE -o $GPFS_BACKUP_CONF  
    if [ $? -ne 0 ]; then
	    up_err_and_exit "Could not save GPFS backup config" 
    fi 
	echo_green "OK"

    # 2. Create filesystem snapshot
    echo "Create snapshot..."
    mmcrsnapshot $GPFS_DEVICE $GPFS_SNAPSHOT -j ${__GPFS_FILESET__}
    if [ $? -ne 0 ]; then
     # Could not create snapshot, something is wrong
	    up_err_and_exit "Could not create snapshot $GPFS_SNAPSHOT for fileset ${__GPFS_FILESET__}" 
    fi 
	echo_green "OK"

	# 3. TSM-Agent on lta03 will backup snapshot data asynchronously and delete snapshot after it is finished	
    echo "Start remote backup..."
	# TODO: generate log on remote !!!!
    ssh lta03-mpdl "nohup ${__REMOTE_BACKUP_SCRIPT__} $GPFS_SNAPSHOT </dev/null >${__REMOTE_LOG__} 2>&1 &"
    if [ $? -ne 0 ]; then
	    up_err_and_exit "Could not start remote backup" 
    fi 
	echo_green "OK"

    echo -e "Asynchronous backup is OK\n"
		
}

##### START
echo_green "Backup started at $(date)"
START=$(timestamp)

###### CHECK 
if [ ! -d "$DB_BACKUP_DIR"  ]; then
    err_and_exit "Cannot find backup directory: $DB_BACKUP_DIR"
fi

if [ ! -L "${SEAFILE_LATEST_DIR}" ]; then
	err_and_exit "Link $SEAFILE_LATEST_DIR does not exist."
fi

###### GPFS stuff
if [[ $(type mmcrsnapshot) =~ "not found" ]]; then
	err_and_exit "Cannot find GPFS executables: mmcrsnapshot"
fi

#TODO: check GPFS mount, probably more precise method! 
RESULT=$(mount -t gpfs)
if [[ ! "$RESULT" =~ "${GPFS_DEVICE} on /keeper type gpfs" ]]; then
	err_and_exit "Cannot find mounted gpfs: $RESULT" 
fi

# Check for old GPFS snapshot
# If there is one, the last backup didn't finish -> something is wrong: ONLY WARNING!
RESULT=$(mmlssnapshot $GPFS_DEVICE -j ${__GPFS_FILESET__}) 
if [[ ! "$RESULT" =~ "No snapshots in file system" ]]; then
    # The way to find at least one snapshot for the fileset. This is not implemented directly in mmlssnapshot, 
    # see https://www.ibm.com/support/knowledgecenter/STXKQY_4.2.0/com.ibm.spectrum.scale.v4r2.adm.doc/bl1adm_mmlssnapshot.htm
    RESULT=$(echo -e "$RESULT" | grep -vwE "^(Snapshots|Directory)" | rev | grep -Eo '^\s*[^ ]+' | rev) 
    if [[ "$RESULT" =~ "${__GPFS_FILESET__}" ]]; then
        # Old snapshot still exists, something is wrong
        #err_and_exit "Old snapshots still exist" 
        warn "Old snapshots still exist! Please clean them up!"
    fi
fi

check_object_storage_integrity

##### END CHECK

shutdown_seafile

backup_databases

#rsync -aLPWz ${SEAFILE_DIR}/seafile-data ${BACKUP_DIR}
#echo_green "Seafile object storage backup is OK"

asynchronous_backup

startup_seafile

echo_green "Backup ended at $(date)"
echo_green "Elapsed time in seconds: $(($(timestamp) - $START))"

echo_green "Backup is successful!"

exit 0


