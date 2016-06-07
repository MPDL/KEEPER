#!/bin/bash
set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
BACKUP_POSTFIX="_orig"
EXT_DIR=$(dirname $(dirname $(readlink -f $0)))
PROPERTIES_FILE=${EXT_DIR}/keeper-qa.properties
BACKUP_DIR=/keeper/test@lta02/backup/databases

PATH=$PATH:/usr/lpp/mmfs/bin
export PATH
TODAY=`date '+%Y%m%d'`
GPFS_DEVICE="gpfs_keeper"
GPFS_SNAPSHOT="mmbackupSnap${TODAY}"

# DEPENDENCY: for usage of nginx_dissite/nginx_ensite, install https://github.com/perusio/nginx_ensite
HTTP_CONF=keeper.conf
MAINTENANCE_HTTP_CONF=keeper_maintenance.conf
HTTP_CONF_ROOT_DIR=/etc/nginx

function err_and_exit () {
	if [ "$1" ]; then
		echo "$(tput setaf 1)Error: ${1}$(tput sgr0)"
		# TODO: send notification 
	fi
	exit 1;
}

function check_file () {
    if [ ! -f "$1" ]; then
		if [ -n "$2" ]; then
			err_and_exit "$2"
		fi
        err_and_exit "Cannot find file $1"
    fi
}

function up_err_and_exit () {
	startup_seafile
	err_and_exit "$1"
}


function echo_green () {
	echo -e "$(tput setaf 2)${1}$(tput sgr0)"
}

# switch HTTP configurations between default and maintenance
function switch_http_server_default_and_maintenance_confs () {
	local TO_DIS="$MAINTENANCE_HTTP_CONF"
	local TO_EN="$HTTP_CONF" 
	
	if [ -L "$HTTP_CONF_ROOT_DIR/sites-enabled/$TO_EN" ]; then
		TO_DIS="$HTTP_CONF"
		TO_EN="$MAINTENANCE_HTTP_CONF"
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
	sh ./seafile-server.sh stop
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot stop seafile"
	fi
	echo_green "OK"
	popd
}

function startup_seafile () {
	pushd $SEAFILE_DIR/scripts
	echo -e "Startup seafile...\n"
	sh ./seafile-server.sh start
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
	/bin/bash ./seaf-fsck.sh
	if [ $? -ne 0  ]; then
		err_and_exit "Object storage integrity test has failed"
	fi
	popd
}


function asynchronous_backup () {
	
    echo -e "Start asynchronous backup...\n"
	# 0. Check for old snapshot
	# If there is one, the last backup didn't finish -> something is wrong
	local RESULT=$(mmlssnapshot $GPFS_DEVICE -s all)
	if [[ ! "$RESULT" =~ "No snapshots in file system" ]]; then
		# Old snapshot still exists, something is wrong
		up_err_and_exit "Old snapshot(s) still existi(s)" 
	fi
	
    # 2. Create filesystem snapshot
	echo "Create snapshot..."
    mmcrsnapshot $GPFS_DEVICE $GPFS_SNAPSHOT
    if [ $? -ne 0 ]; then
     # Could not create snapshot, something is wrong
	    up_err_and_exit "Could not create snapshot $GPFS_SNAPSHOT" 
    fi 
	echo_green "OK"

	# 3. TSM-Agent on lta03 will backup snapshot data asynchronously and delete snapshot after it is finished	
    echo "Start remote backup..."
	# TODO: generate log on remote !!!!
    #ssh lta03-mpdl "/bin/bash /opt/tivoli/tsm/client/ba/bin/do_mmbackup_vlad $GPFS_SNAPSHOT &"
    #if [ $? -ne 0 ]; then
#	    up_err_and_exit "Could not start remote backup" 
#    fi 
#	echo_green "OK"

    echo -e "Asynchronous backup is OK\n"
		
}

##### START

# check keeper environment
if [ ! -d "$BACKUP_DIR"  ]; then
	err_and_exit "Cannot find backup directory: $BACKUP_DIR"
fi

if [ ! -L "${SEAFILE_LATEST_DIR}" ]; then
	err_and_exit "Link $SEAFILE_LATEST_DIR does not exist."
fi

check_file "$PROPERTIES_FILE"

source $PROPERTIES_FILE
if [ $? -ne 0  ]; then
	err_and_exit "Cannot intitialize variables"
fi

if [ ! $(type -P "nginx_ensite") ]; then
	err_and_exit "Please install nginx_[en|dis]site: https://github.com/perusio/nginx_ensite"
fi

if [ ! $(type -P "mmcrsnapshot") ]; then
	err_and_exit "Cannot find GPFS executables: mmcrsnapshot"
fi
#TODO: check GPFS mount, probably preciser method! 
RESULT=$(mount -t gpfs)
if [[ ! "$RESULT" =~ "/dev/gpfs_keeper on /keeper type gpfs" ]]; then
	# Old snapshot still exists, something is wrong
	err_and_exit "Cannot find mounted gpfs: $RESULT" 
fi

check_object_storage_integrity

shutdown_seafile

echo -e "Backup seafile database...\n"
for i in ccnet seafile seahub; do
# TODO: gzip sql	
#	mysqldump -h${__DB_HOST__} -u${__DB_USER__} -p${__DB_PASSWORD__} --verbose ${i}-db > ${BACKUP_DIR}/${i}-db.sql.`date +"%Y-%m-%d-%H-%M-%S"`
	mysqldump -h${__DB_HOST__} -u${__DB_USER__} -p${__DB_PASSWORD__} --verbose ${i}-db | gzip > ${BACKUP_DIR}/`date +"%Y-%m-%d"`.${i}-db.sql.gz
	if [ $? -ne 0  ]; then
		up_err_and_exit "Cannot dump ${i}-db"
	fi
done
echo_green "Database backup is OK"

#rsync -aLPWz ${SEAFILE_DIR}/seafile-data ${BACKUP_DIR}
#echo_green "Seafile object storage backup is OK"

asynchronous_backup

startup_seafile

echo_green "Backup is successful!"

exit 0

