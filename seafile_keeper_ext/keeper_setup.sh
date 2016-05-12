#!/bin/bash

# Set seafile root directory
SEAFILE_DIR=/opt/seafile
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
CUSTOM_DIR=${SEAFILE_DIR}/seahub-data/custom
CUSTOM_LINK=${SEAFILE_LATEST_DIR}/seahub/media/custom
BACKUP_POSTFIX="_orig"
EXT_DIR=$(dirname $(readlink -f $0))

function err_and_exit () {
    if [ "$1" ]; then
        echo "Error: $1"
    fi
    exit 1;
}

function create_custom_link () {
    if [ -L "$CUSTOM_LINK" ]; then
        echo "Link $CUSTOM_LINK already exists, skipping!"
    else
        if [ ! -d $CUSTOM_DIR ]; then
            err_and_exit "$CUSTOM_DIR does not exist"
        else 
            ln -sv $CUSTOM_DIR $CUSTOM_LINK 
            if [ $? -ne 0  ]; then
                err_and_exit "Cannot create link to $CUSTOM_DIR"
            fi
        fi
    fi
}

function remove_custom_link () {
    if [ -L "$CUSTOM_LINK" ]; then
        rm -v $CUSTOM_LINK
    fi
}

function create_custom_link () {
    if [ -L "$CUSTOM_LINK" ]; then
        echo "Link $CUSTOM_LINK already exists, skipping!"
    else
        if [ ! -d $CUSTOM_DIR ]; then
            err_and_exit "$CUSTOM_DIR does not exist"
        else 
            ln -sv $CUSTOM_DIR $CUSTOM_LINK 
            if [ $? -ne 0  ]; then
                err_and_exit "Cannot create link to $CUSTOM_DIR"
            fi
        fi
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

# Files of directories to be overridden
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

function deploy_file () {
    if [ ! -f "$1" ]; then
        err_and_exit "File does not exist: $1"
    fi
    local DEST_FILE=$SEAFILE_DIR/$1
    #if backup does not exist make it
    backup_file $DEST_FILE
    cp -av $1 $DEST_FILE 
    if [ $? -ne 0  ]; then
        err_and_exit "Cannot copy $1 to $DEST_FILE"
    fi
}


function backup_file () {
    if [ ! -f "$1"  ]; then
        err_and_exit "File does not exist: $1"
    fi
    local DEST_FILE=${1}${BACKUP_POSTFIX}
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

case "$1" in
    deploy-all)
        create_and_deploy_directories "scripts" "seahub-data"
        create_custom_link
        deploy_directories "seafile-server-latest"
    ;;

    deploy)
        [ -z "$2" ] && ($0 || exit 1 )
        deploy_file $2
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
        echo "Usage: $0 {deploy-all|deploy <file-name>|restore|clean-all|compile-i18n}"
        exit 1
     ;;
esac

exit 0
