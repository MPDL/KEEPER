#!/bin/bash
#set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
BACKUP_POSTFIX="_orig"

PATH=$PATH:/usr/lpp/mmfs/bin
export PATH
TIMESTAMP=$(date +"%Y-%m-%d_%H:%M:%S")
TODAY=`date '+%Y%m%d'`
WEEKDAY=`date '+%u'`
DAYOFMONTH=`date '+%d'`
GPFS_DEVICE="app-keeper"
GPFS_SNAPSHOT="mmbackupSnap${TODAY}"
CLEANUP_SNAPSHOTS=1
SHADOW_DB_REBUILD_DAY=7
DB_BACKUP_DIR=/keeper/db-backup

MY_BACKUP_PID_FILE="${SEAFILE_LATEST_DIR}/runtime/backup.$$.pid"
#remove PID on EXIT
trap "rm -f -- '$MY_BACKUP_PID_FILE'" EXIT

DEBUG=0

if [ $DEBUG -ne 1 ]; then
    exec > >(tee -a /var/log/keeper/keeper_backup.`date '+%Y-%m-%d'`.log)
    exec 2>&1 
fi

# INJECT ENV
source "${SEAFILE_DIR}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi


function backup_databases () {

    echo -e "Backup seafile databases...\n"

    # clean up old database dumps
    if [ "$(ls -A $DB_BACKUP_DIR)" ]; then
        echo "Clean ${DB_BACKUP_DIR}..."
        rm -v ${DB_BACKUP_DIR}/*
        [ $? -ne 0 ] && err_and_exit "Cannot clean up ${DB_BACKUP_DIR}"
    fi
    for i in ccnet seafile seahub keeper; do
        mysqldump -h${__DB_HOST__} -u${__DB_USER__} -p${__DB_PASSWORD__} -P${__DB_PORT__} --verbose ${i}-db | gzip > ${DB_BACKUP_DIR}/${TIMESTAMP}.${i}-db.sql.gz
        [ $? -ne 0  ] && err_and_exit "Cannot dump ${i}-db"
    done
    echo_green "Databases backup is OK"

}

function cleanup_old_snapshots () {
   
    # Clean up old snapshots, leave at least LATEST_SN_COUNT latest snapshots 
    LATEST_SN_COUNT=3
    if [ $CLEANUP_SNAPSHOTS -eq 1 ]; then
        echo -e "Clean up old snapshots...\n"
        SNAPSHOTS=($(mmlssnapshot $GPFS_DEVICE | tail -n +3 | cut -d' ' -f1 | sort -r))
        if [ -n "$SNAPSHOTS" ]; then
            for SN in "${SNAPSHOTS[@]:$LATEST_SN_COUNT}"; do
                CMD="mmdelsnapshot $GPFS_DEVICE $SN"
                #echo $CMD
                eval "$CMD"
            done
        else 
            warn "No snapshots on $GPFS_DEVICE"
        fi
        echo_green "Clean up of old snapshots is OK"
    fi
}

function backup_object_storage () {
	
    echo -e "Start Object Storage backup...\n"

	# 1. Backup GPFS-Config
    echo "Save GPFS backup config..."
    GPFS_BACKUP_CONF="/keeper/gpfs.config"
    # remove old one if exists
    [[ -e $GPFS_BACKUP_CONF ]] && rm -v $GPFS_BACKUP_CONF
    # save current
    mmbackupconfig $GPFS_DEVICE -o $GPFS_BACKUP_CONF  
    if [ $? -ne 0 ]; then
	    err_and_exit "Could not save GPFS backup config" 
    fi 
	echo_green "OK"

    # 2. Create filesystem snapshot
    echo "Create snapshot..."
    mmcrsnapshot $GPFS_DEVICE $GPFS_SNAPSHOT 
    if [ $? -ne 0 ]; then
     # Could not create snapshot, something is wrong
	    err_and_exit "Could not create snapshot $GPFS_SNAPSHOT" 
    fi 
	echo_green "OK"

    echo "Start TSM  backup..."
    LOGLEVEL="-L 2"
    export MMBACKUP_DSMC_BACKUP="-auditlogging=full -auditlogname=/var/log/mmbackup/tsm-auditlog-$DAYOFMONTH.log"
    export MMBACKUP_DSMC_EXPIRE="-auditlogging=full -auditlogname=/var/log/mmbackup/tsm-auditlog-$DAYOFMONTH.log"
    # Full backup the first time:
    #mmbackup /keeper --scope inodespace --noquote -s /var/tmp -v -t full -B 1000 $LOGLEVEL -m 8 -S $GPFS_SNAPSHOT 

    # on Sunday
    if [ "$WEEKDAY" = $SHADOW_DB_REBUILD_DAY ]; then
      # Rebuild the shadow database on Sundays
        mmbackup /keeper --noquote -s /var/tmp -v -q -t incremental -B 1000 $LOGLEVEL -m 8 -a 1 -S $GPFS_SNAPSHOT 
        [ $? -ne 0 ] && warn "Incremental TSM backup with rebuild of shadow DB is failed" || echo_green "OK"

    else
      # Normal incremental backup on other days
        mmbackup /keeper --scope inodespace --noquote -s /var/tmp -v -t incremental -B 1000 $LOGLEVEL -m 8 -a 1 -S $GPFS_SNAPSHOT 
        [ $? -ne 0 ] && warn "Incremental TSM backup is failed" || echo_green "OK"
    fi

    cleanup_old_snapshots

    echo_green "Object Storage backup is OK\n"
		
}

#sleep 600
#exit 0

##### START
echo_green "Backup started at $(date)"
START=$(timestamp)

###### CHECK 
#keeper is already running!
if [  $(find "${SEAFILE_LATEST_DIR}/runtime" -name "backup.*.pid" )  ]; then
    err_and_exit "Keeper backup process is already running, please check!"
fi

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

# Exit if there is a snapshot today. 
RESULT=$(mmlssnapshot ${GPFS_DEVICE} | tail -n +3 | cut -d' ' -f1 | grep ${GPFS_SNAPSHOT} -q)
if [ $? -eq 0 ]; then
    err_and_exit "Cannot create snapshot $GPFS_SNAPSHOT: the snapshot exists already." 
fi 
##### END CHECK

#create PID file
echo $$ > "$MY_BACKUP_PID_FILE"

backup_databases

backup_object_storage


echo_green "Backup ended at $(date)"
echo_green "Elapsed time: $(elapsed_time ${START})\n"

echo_green "Backup is successful!"

exit 0


