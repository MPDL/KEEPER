#!/bin/bash
#set -x
# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
CUSTOM_DIR=${SEAFILE_DIR}/seahub-data/custom
CUSTOM_LINK=${SEAFILE_LATEST_DIR}/seahub/media/custom
AVATARS_LINK=${SEAFILE_LATEST_DIR}/seahub/media/avatars
BACKUP_POSTFIX="_orig"
EXT_DIR=$(dirname $(readlink -f $0))

# The string should be put on top of files which should be merged manually
MERGE_MANUALLY_STRING="# !!!MERGE MANUALLY!!!"

# INJECT ENV
source "${EXT_DIR}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

function check_consistency () {
	# check link SEAFILE_LATEST_DIR existence
	if [ ! -L "${SEAFILE_LATEST_DIR}" ]; then
        err_and_exit "Link $SEAFILE_LATEST_DIR does not exist, exiting!"
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

# 
# /migrate avatars storage See http://manual.seafile.com/faq.html:
# Q: Avatar pictures vanished after upgrading the server, what can I do? 

function migrate_avatars () {
    # check default installation
    local D=${SEAFILE_LATEST_DIR}/seahub/media/avatars
    if [ -d "$D" ]; then
        #if $D is directory, i.e. installation keeper from scratch 
        #1) create dir backup
        mv -v $D ${D}${BACKUP_POSTFIX}
        if [ $? -ne 0  ]; then
            err_and_exit "Cannot backup $D"
        fi
        #2) create link to CUSTOM avatar link
        #ln -s $D $AVATARS_LINK 
        ln -s $CUSTOM_DIR/../avatars $AVATARS_LINK
        if [ $? -ne 0  ]; then
            err_and_exit "Cannot create $AVATARS_LINK"
        fi
		#TODO: check||create link to avatar in gpfs_keeper fileset
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
	check_file "$1"
	if [ "$(head -n 1 $1)" = "$MERGE_MANUALLY_STRING" ]; then
		echo_red "WARNING: File $DEST_FILE should be merged with ${DEST_FILE}${BACKUP_POSTFIX} manually!!!, e.g.\nvimdiff -R ${DEST_FILE} -c ':se noreadonly' ${DEST_FILE}${BACKUP_POSTFIX}" 
	fi
}

# Deploy directories
function deploy_directories () {
    for i in "$@"; do
        echo "Deploy directory <$i>"
        local DEST_DIR=$SEAFILE_DIR/$i
        if [ ! -d "$DEST_DIR" ]; then
            err_and_exit "Directory does not exist: $DEST_DIR"
        else
            local SOURCE_FILES=( $(find -H $i -type f ! -iname "*.pyc" ! -path "*/.ropeproject/*" ! -path "*/.cache/*" ! -iname ".gitignore") )
            for f in "${SOURCE_FILES[@]}"; do
                deploy_file $f
           done
       fi
    done
}

# Files of directories to be created
function create_and_deploy_directories () {
    for i in "$@"; do
        local DEST_DIR=$SEAFILE_DIR/$i
        if [ -d "$DEST_DIR" ]; then
           echo "$DEST_DIR already exists, skipping!"
        else
            echo "Create directory <$i>"
            mkdir $DEST_DIR
            if [ $? -ne 0  ]; then
                err_and_exit "Cannot create dir: $DEST_DIR"
            fi
        fi    
        deploy_directories "$i"
    done
}

# Deploy conf/ directory
function deploy_conf () {
	check_file "$PROPERTIES_FILE" "Cannot find properties file $PROPERTIES_FILE for the instance"
	for i in seahub_settings.py ccnet.conf seafile.conf seafevents.conf seafdav.conf; do 
		deploy_file "conf/$i" "-p" "$PROPERTIES_FILE"
    done
}


# Deploy HTTP confs and maintenance stuff 
deploy_http_conf () {
	# deploy http maintenance conf 
	
    for F in ${__MAINTENANCE_HTTP_CONF__} ${__HTTP_CONF__} ; do
		local DEST_FILE="${__HTTP_CONF_ROOT_DIR__}/sites-available/$F" 
		if [ -f "$DEST_FILE" ]; then
			echo "Config already exists: $DEST_FILE, skipping!"
		else  
			expand_properties_and_deploy_file "${EXT_DIR}/http/$F" "$PROPERTIES_FILE" "$DEST_FILE"
		fi
	done 

	DEST_FILE="${__HTML_DEFAULT_DIR__}/${__MAINTENANCE_HTML__}"
	if [ -f "$DEST_FILE" ]; then
        echo "Html already exists: $DEST_FILE, skipping!"
	else  
		deploy_file "$EXT_DIR/http/${__MAINTENANCE_HTML__}" "$DEST_FILE"
	fi
}

# create dir for file if not exists
function create_dir_for_file () {
    DEST_DIR=$(dirname $1)
    if [ ! -d "$DEST_DIR" ]; then
        mkdir -p $DEST_DIR
        if [ $? -ne 0  ]; then
            err_and_exit "Cannot create dir $DEST_DIR"
        fi
    fi
}

# Deploy single file
function deploy_file () {
	
	# at least one paramater and should be a path to file
	check_file "$1"
	# default destination is seafile dirs
	local DEST_FILE="$SEAFILE_DIR/$1"
	# if second parameter defined and is not -p, it is an absolute path
	if [ -n "$2" ] && [ "$2" != "-p" ]; then
		DEST_FILE=$2
	fi	
    if [ ! -f "$DEST_FILE" ]; then
 	    read -p "Deploy file $1 into $DEST_FILE (y/n)?" choice
	    case "$choice" in 
		    y|Y ) echo "yes";;
		    n|N ) return;;
		    * ) echo "invalid";return;;
	    esac
    else
	    backup_file $DEST_FILE
    fi	    

	# expand properties
	if [ "$2" = "-p" ] && [ -f "$3" ]; then
		expand_properties_and_deploy_file $1 $3 $DEST_FILE
	else
        create_dir_for_file $DEST_FILE
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
	local RESULT=`cat -v $PROPS_FILE | sed -e 's/#.*$//' -e '/^$/d' | awk -F= '{print "s#" $1 "#" $2 "#g"}' | sed -f - $IN`
	if [ -z "$RESULT" ]; then 
		err_and_exit "Cannot expand properties $PROPS_FILE for $IN"
	fi
    create_dir_for_file $OUT
    echo "$RESULT" >$OUT
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot deploy expanded file $IN to $OUT"
	else 
		echo " File $IN expanded with $PROPS_FILE and copied to $OUT"	
	fi
}


# Backup file 
function backup_file () {
	check_file "$1"
    local BACKUP_FILE=${1}${BACKUP_POSTFIX}
    #if file already exists, do not backup it
    if [ -f "$BACKUP_FILE" ]; then
        echo "Backup already exists: $BACKUP_FILE, skipping!"
    else
        echo "Backup $1"
        mv -v $1 $BACKUP_FILE
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

# Overwrites keeper EXT files with the seafiles sources. 
# This is part of migration procedure, see https://keeper.mpdl.mpg.de/lib/a0b4567a-8f72-4680-8a76-6100b6ebbc3e/file/Keeper%20System%20Administration/Migration.md
function copy_seaf_src_to_ext() {
    pushd $EXT_DIR/seafile-server-latest
    TARGET_FILES=( $(find -H . -type f -not \( -path "*/.rope*" -or -path "*/__pycache*" -or -path "*/.cache*" -or -path "*/.git*" -or -path "*/tags" -or -name "*.pyc" -or -path "*/keeper*" \) ) )
    echo "$TARGET_FILES"
    for i in "${TARGET_FILES[@]}"; do
        local SRC_FILE="${SEAFILE_LATEST_DIR}/${i}" 
        [ -f "$SRC_FILE" ] && cp -v "$SRC_FILE" "${i}"
    done
    popd
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
		deploy_http_conf
        migrate_avatars
    ;;

    deploy-conf)
        deploy_conf  
	;;

    deploy-http-conf)
        deploy_http_conf 
	;;

    deploy)
        [ -z "$2" ] && ($0 || exit 1 )
        deploy_file $2 $3 $4
    ;;

    deploy-dir)
        [ -z "$2" ] && ($0 || exit 1 )
        deploy_directories "${@:2}"
    ;;

    restore)
        restore_directories "seafile-server-latest"
        remove_custom_link
    ;;

    clean-all)
        $0 restore
        rm -rfv $SEAFILE_DIR/seahub-data
    ;;

    compile-i18n)
        pushd $SEAFILE_LATEST_DIR/seahub
        ./i18n.sh compile-all
        popd
    ;;

    copy-seafile-sources-in-ext)
         copy_seaf_src_to_ext   
    ;;
    
    min.css)
        pushd $SEAFILE_LATEST_DIR/seahub/media/css
        yui-compressor -v seahub.css -o seahub.min.css
        popd
    ;;
 

    *)
        echo "Usage: $0 {deploy-all|deploy-conf|deploy-http-conf|deploy <file> [-p <properties-file>]|deploy-dir <dir>|restore|clean-all|compile-i18n|copy-seafile-sources-in-ext|min.css}"
        exit 1
     ;;
esac

exit 0
