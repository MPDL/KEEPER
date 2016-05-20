#!/bin/bash
#set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
BACKUP_POSTFIX="_orig"
EXT_DIR=$(dirname $(dirname $(readlink -f $0)))
PROPERTIES_FILE=${EXT_DIR}/keeper-prod.properties
BACKUP_DIR=/keeper/backup/databases

function err_and_exit () {
if [ "$1" ]; then
	echo "$(tput setaf 2)Error: ${1}$(tput sgr0)"
fi
exit 1;
}

function echo_green () {
	echo -e "$(tput setaf 2)${1}$(tput sgr0)"
}

if [ ! -d "$BACKUP_DIR"  ]; then
	err_and_exit "Cannot find backup directory: $BACKUP_DIR"
fi

if [ ! -f "$PROPERTIES_FILE"  ]; then
	err_and_exit "Cannot find KEEPER properties file $PROPERTIES_FILE"
fi

source $PROPERTIES_FILE
if [ $? -ne 0  ]; then
	err_and_exit "Cannot intitialize variables"
fi

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

echo_green "Backup is successful!"

exit 0

