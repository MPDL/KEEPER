#!/bin/bash
#set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
BACKUP_POSTFIX="_orig"

PATH=$PATH:/usr/lpp/mmfs/bin
export PATH
TODAY=`date '+%Y%m%d'`
GPFS_DEVICE="app-keeper"
GPFS_SNAPSHOT="mmbackupSnap${TODAY}"
REMOVE_SNAPSHOT=0


exec > >(tee /var/log/keeper/keeper_backup.`date '+%Y-%m-%d'`.log)
exec 2>&1 


# INJECT ENV
source "${SEAFILE_DIR}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

DB_BACKUP_DIR=/keeper/db-backup


function backup_databases () {

    echo -e "Backup seafile databases...\n"

    # clean up old databases
    #if [ "$(ls -A $DB_BACKUP_DIR)" ]; then
        #echo "Clean ${DB_BACKUP_DIR}..."
        #rm -v ${DB_BACKUP_DIR}/*
        #[ $? -ne 0 ] && up_err_and_exit "Cannot clean up ${DB_BACKUP_DIR}"
    #fi
    local TIMESTAMP=$(date +"%Y-%m-%d_%H:%M:%S")
    for i in ccnet seafile seahub keeper; do
        mysqldump -h${__DB_HOST__} -u${__DB_USER__} -p${__DB_PASSWORD__} -P${__DB_PORT__} --verbose ${i}-db | gzip > ${DB_BACKUP_DIR}/${TIMESTAMP}.${i}-db.sql.gz
        [ $? -ne 0  ] && up_err_and_exit "Cannot dump ${i}-db"
    done
    echo_green "Databases backup is OK"

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
	    up_err_and_exit "Could not save GPFS backup config" 
    fi 
	echo_green "OK"

    # 2. Create filesystem snapshot
    echo "Create snapshot..."
    mmcrsnapshot $GPFS_DEVICE $GPFS_SNAPSHOT 
    if [ $? -ne 0 ]; then
     # Could not create snapshot, something is wrong
	    up_err_and_exit "Could not create snapshot $GPFS_SNAPSHOT" 
    fi 
	echo_green "OK"

    echo "Start TSM  backup..."
    # Full backup the first time:
    mmbackup /keeper --scope inodespace --noquote -s /var/tmp -v -t full -B 1000 -L 6 -m 8 -S $GPFS_SNAPSHOT 

    #if [ "$WEEKDAY" = 7 ]; then
      ## Rebuild the shadow database on Sundays
        #mmbackup /keeper --scope inodespace --noquote -s /var/tmp -v -q -t incremental -B 1000 -L 6 -m 8 -a 1 -S $GPFS_SNAPSHOT
        #if [ $? -ne 0 ]; then
            #up_err_and_exit "TSM backup failed" 
        #fi 
    #else
      ## Normal incremental backup on other days
        #mmbackup /keeper --scope inodespace --noquote -s /var/tmp -v -t incremental -B 1000 -L 6 -m 8 -a 1 -S $GPFS_SNAPSHOT 
        #if [ $? -ne 0 ]; then
            #up_err_and_exit "TSM backup failed" 
        #fi 
    #fi
    #echo_green "OK"

    #if [ $REMOVE_SNAPSHOT -eq 1 ]; then
        #mmdelsnapshot $GPFS_DEVICE $SNAPSHOT
    #fi

    echo -e "Object Storage backup is OK\n"
		
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
RESULT=$(mmlssnapshot $GPFS_DEVICE) 
if [[ ! "$RESULT" =~ "No snapshots in file system" ]]; then
    warn "Old snapshots still exist! Please clean them up!"
fi

##### END CHECK

#shutdown_seafile

backup_databases

backup_object_storage


echo_green "Backup ended at $(date)"
echo_green "Elapsed time: $(elapsed_time ${START})\n"

echo_green "Backup is successful!"

exit 0


