#!/bin/bash
#set -x
# Set seafile root directory
SEAFILE_DIR=__SEAFILE_DIR__
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
BACKUP_POSTFIX="_orig"

PATH=$PATH:/usr/lpp/mmfs/bin
export PATH
TODAY=`date '+%Y%m%d'`
WEEKDAY=`date '+%u'`
DAYOFMONTH=`date '+%d'`
GPFS_SNAPSHOT="mmbackupSnap${TODAY}"
CLEANUP_SNAPSHOTS=1
SHADOW_DB_REBUILD_DAY=7
DB_BACKUP_DIR=/keeper/db-backup

RECOVERY_COMMANDS=()

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


function get_timestamp() {
    echo $(date +"%Y-%m-%d %H:%M:%S")
}

function backup_databases () {

    echo -e "Backup seafile databases...\n"

    # clean up old database dumps
    if [ "$(ls -A $DB_BACKUP_DIR)" ]; then
        echo "Clean ${DB_BACKUP_DIR}..."
        rm -v ${DB_BACKUP_DIR}/*
        [ $? -ne 0 ] && err_and_exit "Cannot clean up ${DB_BACKUP_DIR}"
    fi
    MYSQLDUMP_START_TIME=$(get_timestamp)
    echo "Start time of first mysqldump: ${MYSQLDUMP_START_TIME}"
    for i in ccnet seafile seahub keeper; do
        TIMESTAMP=$(get_timestamp | tr ' ' '_')
        mysqldump -h${__DB_HOST__} -u${__DB_USER__} -p${__DB_PASSWORD__} -P${__DB_PORT__} --verbose ${i}-db | gzip > ${DB_BACKUP_DIR}/${TIMESTAMP}.${i}-db.sql.gz
        [ $? -ne 0  ] && err_and_exit "Cannot dump ${i}-db"
        RECOVERY_COMMANDS+=(echo "mysql -u${__DB_USER__} -p${__DB_PASSWORD__} -P${__DB_PORT__} ${i} < ${DB_BACKUP_DIR}/${TIMESTAMP}.${i}-db.sql.gz")
    done
    echo_green "Databases backup is OK"

}

function cleanup_old_snapshots () {
   
    # Clean up old snapshots, leave at least LATEST_SN_COUNT latest snapshots 
    LATEST_SN_COUNT=3
    if [ $CLEANUP_SNAPSHOTS -eq 1 ]; then
        echo -e "Clean up old snapshots...\n"
        SNAPSHOTS=($(mmlssnapshot ${__GPFS_DEVICE__} | tail -n +3 | cut -d' ' -f1 | sort -r))
        if [ -n "$SNAPSHOTS" ]; then
            for SN in "${SNAPSHOTS[@]:$LATEST_SN_COUNT}"; do
                CMD="mmdelsnapshot ${__GPFS_DEVICE__} $SN"
                #echo $CMD
                eval "$CMD"
            done
        else 
            warn "No snapshots on ${__GPFS_DEVICE__}"
        fi
        echo_green "Clean up of old snapshots is OK"
    fi
}


function do_tsm_backup () {

    if [ "${__SKIP_TSM_BACKUP__}" != "True" ]; then
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
        echo_green "OK"
    else    
        echo_green "Skipping TSM backup"
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
    mmbackupconfig ${__GPFS_DEVICE__} -o $GPFS_BACKUP_CONF  
    if [ $? -ne 0 ]; then
	    err_and_exit "Could not save GPFS backup config" 
    fi 
	echo_green "OK"

    # 2. Create filesystem snapshot
    echo "Create snapshot..."
    
    #check GPFS status before 
    mmdf ${__GPFS_DEVICE__} 
    
    mmcrsnapshot ${__GPFS_DEVICE__} $GPFS_SNAPSHOT 
    if [ $? -ne 0 ]; then
     # Could not create snapshot, something is wrong
	    err_and_exit "Could not create snapshot $GPFS_SNAPSHOT" 
    fi 
	echo_green "OK"


    SNAPSHOT_CREATION_END_TIME=$(get_timestamp)
    echo "Snapshot creation time: $SNAPSHOTS_CREATION_TIME"
    
    #Generate DB recovery commands 
    BIN_LOGS_DIR="/keeper/.snapshots/${GPFS_SNAPSHOT}/mysql/logs"
    NEWEST_BIN_FILE=$(find $BIN_LOGS_DIR -type f -name "*.[0-9]*" -printf "%T@ %p\n" | sort -n | tail -1 | cut -f 2 -d ' ')
    RECOVERY_COMMANDS+=("mysql --start-datetime=\"${MYSQLDUMP_START_TIME}\" --stop-datetime=\"${SNAPSHOT_CREATION_END_TIME}\" ${BIN_LOGS_DIR}/${NEWEST_BIN_FILE} |  mysql -u root -p")
    RECOVERY_COMMANDS+=("CHECK CONTENT: mysqlbinlog --start-datetime=\"${MYSQLDUMP_START_TIME}\" --stop-datetime=\"${SNAPSHOT_CREATION_END_TIME}\" --base64-output=decode-rows --verbose ${BIN_LOGS_DIR}/${NEWEST_BIN_FILE} > decoded.txt")

    #check GPFS status after 
    mmdf ${__GPFS_DEVICE__} 

    do_tsm_backup

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
if [[ ! "$RESULT" =~ "${__GPFS_DEVICE__} on /keeper type gpfs" ]]; then
	err_and_exit "Cannot find mounted gpfs: $RESULT" 
fi

# Exit if there is a snapshot today. 
RESULT=$(mmlssnapshot ${__GPFS_DEVICE__} | tail -n +3 | cut -d' ' -f1 | grep ${GPFS_SNAPSHOT} -q)
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

echo "########################################"
echo "### Recovery commands:\n"
printf '%s\n' "${RECOVERY_COMMANDS[@]}"
echo "########################################"



echo_green "Backup is successful!"

exit 0


