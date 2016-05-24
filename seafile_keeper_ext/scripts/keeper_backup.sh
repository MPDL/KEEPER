#!/bin/bash
#set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
BACKUP_POSTFIX="_orig"
EXT_DIR=$(dirname $(dirname $(readlink -f $0)))
PROPERTIES_FILE=${EXT_DIR}/keeper-prod.properties
BACKUP_DIR=/keeper/backup/databases

# DEPENDENCY: ifor usage of nginx_dissite/nginx_ensite, install https://github.com/perusio/nginx_ensite
HTTP_CONF=keeper.conf
MAINTENANCE_HTTP_CONF=keeper_maintenance.conf
HTTP_CONF_ROOT_DIR=/etc/nginx

function err_and_exit () {
	if [ "$1" ]; then
		echo "$(tput setaf 1)Error: ${1}$(tput sgr0)"
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

	/bin/bash /usr/local/bin/nginx_dissite $TO_DIS
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot disable HTTP config $TO_DIS"
	fi
	
	/bin/bash /usr/local/bin/nginx_ensite $TO_EN
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot enable HTTP config $TO_EN"
	fi

	service nginx reload
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot reload HTTP $TO_EN"
	fi
}


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

# check seafile object storage integrity
pushd $SEAFILE_LATEST_DIR
/bin/bash ./seaf-fsck.sh
if [ $? -ne 0  ]; then
	err_and_exit "Object storage integrity test has failed"
fi

# switch to keeper maintenance HTTP conf
switch_http_server_default_and_maintenance_confs

pushd $SEAFILE_DIR/scripts

echo -e "Shutdown seafile..."
sh ./seafile-server.sh stop
if [ $? -ne 0  ]; then
	err_and_exit "Cannot stop seafile"
fi
echo_green "OK"

echo -e "Backup seafile database...\n"
for i in ccnet seafile seahub; do
	mysqldump -h${__DB_HOST__} -u${__DB_USER__} -p${__DB_PASSWORD__} --verbose ${i}-db > ${BACKUP_DIR}/${i}-db.sql.`date +"%Y-%m-%d-%H-%M-%S"`
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot dumb DB ${i}-db"
	fi
done
echo_green "Database backup is OK"


echo -e "Backup seafile object storage...\n"
rsync -aLPWz ${SEAFILE_DIR}/seafile-data ${BACKUP_DIR}
echo_green "Seafile object storage backup is OK"

echo -e "Startup seafile...\n"
sh ./seafile-server.sh start
if [ $? -ne 0  ]; then
	err_and_exit "Cannot start seafile"
fi
echo_green "OK"

popd
popd

# switch back to keeper HTTP conf
switch_http_server_default_and_maintenance_confs

echo_green "Backup is successful!"

exit 0

