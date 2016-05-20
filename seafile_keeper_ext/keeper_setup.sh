#!/bin/bash

# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
CUSTOM_DIR=${SEAFILE_DIR}/seahub-data/custom
CUSTOM_LINK=${SEAFILE_LATEST_DIR}/seahub/media/custom
BACKUP_POSTFIX="_orig"
EXT_DIR=$(dirname $(readlink -f $0))
PROPERTIES_FILE=keeper-prod.properties

# The string should be put on top of files which should be merged manually
MERGE_MANUALLY_STRING="# !!!MERGE MANUALLY!!!"


function err_and_exit () {
    if [ "$1" ]; then
        echo "Error: $1"
    fi
    exit 1;
}

function check_consistency () {
	# check link SEAFILE_LATEST_DIR existence
	if [ ! -L "${SEAFILE_LATEST_DIR}" ]; then
        err_and_exit "Link $SEAFILE_LATEST_DIR does not exist, aborting!"
	fi
}


# Create link to custom directory for seafile customization, 
# see http://manual.seafile.com/config/seahub_customization.html
function create_custom_link () {
    if [ -L "$CUSTOM_LINK" ]; then
        echo "Link $CUSTOM_LINK already exists, skipping!"
    else
        if [ ! -d $CUSTOM_DIR ]; then
			echo "$CUSTOM_DIR does not exist, creating"
			mkdir -p "$CUSTOM_DIR"
            if [ $? -ne 0  ]; then
                err_and_exit "Cannot create CUSTOM_DIR"
            fi
		fi	
		ln -sv $CUSTOM_DIR $CUSTOM_LINK 
		if [ $? -ne 0  ]; then
			err_and_exit "Cannot create link to $CUSTOM_DIR"
		fi
	fi
}

# Remove link to custom directory 
function remove_custom_link () {
    if [ -L "$CUSTOM_LINK" ]; then
        rm -v $CUSTOM_LINK
    fi
}

# Check file merging
function check_merging () {
    if [ ! -f "$1" ]; then
        err_and_exit "File does not exist: $1"
    fi
	if [ "$(head -n 1 $1)" = "$MERGE_MANUALLY_STRING" ]; then
		echo -e "$(tput setaf 1)WARNING: File $DEST_FILE should be merged with ${DEST_FILE}${BACKUP_POSTFIX} manually!!!$(tput sgr0), e.g.\nvimdiff -R ${DEST_FILE} -c ':se noreadonly' ${DEST_FILE}${BACKUP_POSTFIX}" 
	fi
	
}

# Files of directories to be created
function create_and_deploy_directories () {
    for i in "$@"; do
        echo "Install directory <$i>"
        local DEST_DIR=$SEAFILE_DIR/$i
        if [ -d "$DEST_DIR" ]; then
           echo "$DEST_DIR already exists, skipping!"
        else
            mkdir $DEST_DIR
            if [ $? -ne 0  ]; then
                err_and_exit "Cannot create dir: $DEST_DIR"
            fi
            local SOURCE_DIR=$EXT_DIR/$i
            cp -arv $SOURCE_DIR/* $DEST_DIR
            if [ $? -ne 0  ]; then
                err_and_exit "Cannot copy files from $SOURCE_DIR to $DEST_DIR"
            fi
        fi
    done
}

# Deploy directories
function deploy_directories  () {
    for i in "$@"; do
        echo "Deploy directory <$i>"
        local DEST_DIR=$SEAFILE_DIR/$i
        if [ ! -d "$DEST_DIR" ]; then
            err_and_exit "Directory does not exist: $DEST_DIR"
        else
            local SOURCE_FILES=( $(find -H $i -type f) )
            for f in "${SOURCE_FILES[@]}"; do
                deploy_file $f
           done
       fi
    done
}

# Deploy conf/ directory
function deploy_conf () {
    if [ ! -f "$PROPERTIES_FILE" ]; then
        err_and_exit "Cannot find properties file $PROPERTIES_FILE for the instance"
    fi
	for i in seahub_settings.py ccnet.conf seafevents.conf seafdav.conf; do 
		deploy_file "conf/$i" "-p" "$PROPERTIES_FILE"
    done
}

# Deploy single file
function deploy_file () {
    if [ ! -f "$1" ]; then
        err_and_exit "File does not exist: $1"
    fi
    local DEST_FILE=$SEAFILE_DIR/$1
    backup_file $DEST_FILE

	# expand properties
	if [ "$2" = "-p" ] && [ -f "$3" ]; then
		expand_properties_and_deploy_file $1 $3 $DEST_FILE
	else	
		cp -av $1 $DEST_FILE 
		if [ $? -ne 0  ]; then
			err_and_exit "Cannot copy $1 to $DEST_FILE"
		fi
	fi
	check_merging $DEST_FILE
}

# Expand properties and deploy file
function expand_properties_and_deploy_file () {
	local IN=$1
	local OUT=$3
	local PROPS_FILE=$2
	# remove commented propeties ------🡓
	local RESULT=`cat -v $PROPS_FILE | sed -e 's/#.*$//' | awk -F= '{print "s/" $1 "/" $2 "/g"}' | sed -f - $IN`
	if [ -z "$RESULT" ]; then 
		err_and_exit "Cannot expand properties $PROPS_FILE for $IN"
	fi
	echo "$RESULT" >$OUT
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot deploy expanded file $IN to $OUT"
	else 
		echo " File $IN expanded with $PROPS_FILE and copied to $OUT"	
	fi
}


# Backup file 
function backup_file () {
    if [ ! -f "$1"  ]; then
        err_and_exit "File does not exist: $1"
    fi
    local DEST_FILE=${1}${BACKUP_POSTFIX}
    #if file already exists, do not backup it
    if [ -f "$DEST_FILE" ]; then
        echo "Backup already exists: $DEST_FILE, skipping!"
    else
        echo "Backup $1"
        mv -v $1 $DEST_FILE
        if [ $? -ne 0  ]; then
            err_and_exit "Cannot backup $1"
        fi
    fi
}


# Restore backup files
function restore_directories () {
    for i in "$@"; do
        echo "Restore directory <$i>"
        local DEST_DIR=$SEAFILE_DIR/$i
        if [ ! -d "$DEST_DIR" ]; then
            err_and_exit "Directory does not exist: $DEST_DIR"
        else
            local SOURCE_FILES=( $(find -H $DEST_DIR -type f -name "*${BACKUP_POSTFIX}") )
            for f in "${SOURCE_FILES[@]}"; do
                local DEST_FILE=${f%${BACKUP_POSTFIX}}
                echo "Restore $f"
                mv -v $f $DEST_FILE
                if [ $? -ne 0  ]; then
                    err_and_exit "Cannot restore file: $DEST_FILE"
                fi
            done
       fi
    done
}

check_consistency

case "$1" in
    deploy-all)
        create_and_deploy_directories "scripts" "seahub-data"
        create_custom_link
        deploy_directories "seafile-server-latest"
        deploy_conf 
	    #TODO: create_server_script_links 	
		$0 compile-i18n
    ;;

    deploy-conf)
        deploy_conf  
	;;

    deploy)
        [ -z "$2" ] && ($0 || exit 1 )
        deploy_file $2 $3 $4
    ;;

    restore)
        restore_directories "seafile-server-latest"
        remove_custom_link
    ;;

    clean-all)
        $0 restore
        rm -rfv $SEAFILE_DIR/scripts $SEAFILE_DIR/seahub-data
    ;;

    compile-i18n)
        pushd $SEAFILE_LATEST_DIR/seahub
        bash ./i18n.sh compile-all
        popd
    ;;


    *)
        echo "Usage: $0 {deploy-all|deploy-conf|deploy <file> [-p <properties-file>]|restore|clean-all|compile-i18n}"
        exit 1
     ;;
esac

exit 0
