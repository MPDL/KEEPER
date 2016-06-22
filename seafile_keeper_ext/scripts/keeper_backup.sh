#!/bin/bash
set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
BACKUP_POSTFIX="_orig"
EXT_DIR=$(dirname $(dirname $(readlink -f $0)))

PATH=$PATH:/usr/lpp/mmfs/bin
export PATH
TODAY=`date '+%Y%m%d'`
GPFS_DEVICE="gpfs_keeper"
GPFS_SNAPSHOT="mmbackupSnap${TODAY}"

# DEPENDENCY: for usage of nginx_dissite/nginx_ensite, install https://github.com/perusio/nginx_ensite
HTTP_CONF_ROOT_DIR=/etc/nginx

function echo_green () {
    if [ "$(tput colors 2>/dev/null)" ]; then 
        echo -e "$(tput setaf 2)${1}$(tput sgr0)"
    else
        echo -e "${1}"
    fi
}

function echo_red () {
    if [ "$(tput colors 2>/dev/null)" ]; then 
        echo -e "$(tput setaf 1)${1}$(tput sgr0)"
    else
        echo -e "${1}"
    fi
}

function err_and_exit () {
	if [ "$1" ]; then
        echo_red "Error: $1"
		# TODO: send notification 
	fi
	exit 1;
}

function up_err_and_exit () {
	startup_seafile
	err_and_exit "$1"
}



function check_file () {
    if [ ! -f "$1" ]; then
		if [ -n "$2" ]; then
			err_and_exit "$2"
		fi
        err_and_exit "Cannot find file $1"
    fi
}

### GET INSTANCE PROPERTIES FILE
# KEEPER instance properties file should be located in SEAFILE_DIR!!!
FILES=( $(find ${SEAFILE_DIR} -maxdepth 1 -type f -name "keeper*.properties") )
( [[ $? -ne 0 ]] || [[ ${#FILES[@]} -eq 0 ]] ) && err_and_exit "Cannot find instance properties file in ${SEAFILE_DIR}"
[[ ${#FILES[@]} -ne 1 ]] && err_and_exit "Too many instance properties files in ${SEAFILE_DIR}:\n ${FILES[*]}"
PROPERTIES_FILE="${FILES[0]}"
source "${PROPERTIES_FILE}"
if [ $? -ne 0  ]; then
	err_and_exit "Cannot intitialize variables"
fi
### END

DB_BACKUP_DIR=/keeper/${__GPFS_FILESET__}/db-backup


# switch HTTP configurations between default and maintenance
function switch_http_server_default_and_maintenance_confs () {
	local TO_DIS="${__MAINTENANCE_HTTP_CONF__}"
	local TO_EN="${__HTTP_CONF__}" 
	
	if [ -L "${HTTP_CONF_ROOT_DIR}/sites-enabled/$TO_EN" ]; then
		TO_DIS="${__HTTP_CONF__}"
		TO_EN="${__MAINTENANCE_HTTP_CONF__}"
	fi	

	nginx_dissite $TO_DIS
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot disable HTTP config $TO_DIS"
	fi
	
	nginx_ensite $TO_EN
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot enable HTTP config $TO_EN"
	fi

	service nginx reload
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot reload HTTP $TO_EN"
	fi
}

function shutdown_seafile () {

	switch_http_server_default_and_maintenance_confs

    pushd $SEAFILE_DIR/scripts
    echo -e "Shutdown seafile..."
    ./seafile-server.sh stop
    if [ $? -ne 0  ]; then
        err_and_exit "Cannot stop seafile"
    fi
    echo_green "OK"
    popd
}

function startup_seafile () {
    pushd $SEAFILE_DIR/scripts
    echo -e "Startup seafile...\n"
    ./seafile-server.sh start
    if [ $? -ne 0  ]; then
        err_and_exit "Cannot start seafile"
    fi
    echo_green "OK"
    popd

	switch_http_server_default_and_maintenance_confs
}

# check seafile object storage integrity
function check_object_storage_integrity () {
    pushd $SEAFILE_LATEST_DIR
    ./seaf-fsck.sh
    if [ $? -ne 0  ]; then
        err_and_exit "Object storage integrity test has failed"
    fi
    popd
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
    for i in ccnet seafile seahub; do
        mysqldump -h${__DB_HOST__} -u${__DB_USER__} -p${__DB_PASSWORD__} --verbose ${i}-db | gzip > ${DB_BACKUP_DIR}/${TIMESTAMP}.${i}-db.sql.gz
        [ $? -ne 0  ] && up_err_and_exit "Cannot dump ${i}-db"
    done
    echo_green "Databases backup is OK"

}

function asynchronous_backup () {
	
    echo -e "Start asynchronous backup...\n"
	
    # 1. Create filesystem snapshot
	echo "Create snapshot..."
    mmcrsnapshot $GPFS_DEVICE $GPFS_SNAPSHOT -j ${__GPFS_FILESET__}
    if [ $? -ne 0 ]; then
     # Could not create snapshot, something is wrong
	    up_err_and_exit "Could not create snapshot $GPFS_SNAPSHOT for fileset ${__GPFS_FILESET__}" 
    fi 
	echo_green "OK"

	# 2. TSM-Agent on lta03 will backup snapshot data asynchronously and delete snapshot after it is finished	
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

###### CHECK 
if [ ! -d "$DB_BACKUP_DIR"  ]; then
    err_and_exit "Cannot find backup directory: $DB_BACKUP_DIR"
fi

if [ ! -L "${SEAFILE_LATEST_DIR}" ]; then
	err_and_exit "Link $SEAFILE_LATEST_DIR does not exist."
fi

RESULT=$(type "nginx_ensite" 2>/dev/null)
if [ $? -ne 0 ] ; then
	err_and_exit "Please install nginx_[en|dis]site: https://github.com/perusio/nginx_ensite"
fi

###### GPFS stuff
if [ ! $(type "mmcrsnapshot") ]; then
	err_and_exit "Cannot find GPFS executables: mmcrsnapshot"
fi
#TODO: check GPFS mount, probably more precise method! 
RESULT=$(mount -t gpfs)
if [[ ! "$RESULT" =~ "/dev/gpfs_keeper on /keeper type gpfs" ]]; then
	# Old snapshot still exists, something is wrong
	err_and_exit "Cannot find mounted gpfs: $RESULT" 
fi

# Check for old GPFS snapshot
# If there is one, the last backup didn't finish -> something is wrong
RESULT=$(mmlssnapshot $GPFS_DEVICE -j ${__GPFS_FILESET__})
if [[ ! "$RESULT" =~ "No snapshots in file system" ]]; then
    # The way to find at least one snapshot for the fileset. This is not implemented directly in mmlssnapshot, 
    # see https://www.ibm.com/support/knowledgecenter/STXKQY_4.2.0/com.ibm.spectrum.scale.v4r2.adm.doc/bl1adm_mmlssnapshot.htm
    RESULT=$(echo -e "$RESULT" | grep -vwE "^(Snapshots|Directory)" | rev | grep -Eo '^\s*[^ ]+' | rev) 
    if [[ "$RESULT" =~ "${__GPFS_FILESET__}" ]]; then
        # Old snapshot still exists, something is wrong
        err_and_exit "Old snapshots still exist" 
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

echo_green "Backup is successful!"

exit 0

