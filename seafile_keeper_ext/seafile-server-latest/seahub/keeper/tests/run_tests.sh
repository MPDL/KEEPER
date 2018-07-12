#!/bin/bash

SEAFILE_DIR=__SEAFILE_DIR__
INSTALLPATH=${SEAFILE_DIR}/seafile-server-latest
default_ccnet_conf_dir=${SEAFILE_DIR}/ccnet
central_config_dir=${SEAFILE_DIR}/conf

#get path of seafile.conf
function read_seafile_data_dir () {
    seafile_ini=${default_ccnet_conf_dir}/seafile.ini
    if [[ ! -f ${seafile_ini} ]]; then
        echo "${seafile_ini} not found. Now quit"
        exit 1
    fi
    seafile_data_dir=$(cat "${seafile_ini}")
    if [[ ! -d ${seafile_data_dir} ]]; then
        echo "Your seafile server data directory \"${seafile_data_dir}\" is invalid or doesn't exits."
        echo "Please check it first, or create this directory yourself."
        echo ""
        exit 1;
    fi
}

read_seafile_data_dir;

export CCNET_CONF_DIR=${default_ccnet_conf_dir}
export SEAFILE_CONF_DIR=${seafile_data_dir}
export SEAFILE_CENTRAL_CONF_DIR=${central_config_dir}
export SEAFES_DIR=${INSTALLPATH}/pro/python/seafes

export PYTHONPATH=${INSTALLPATH}/seafile/lib64/python2.6/site-packages:${INSTALLPATH}/seahub/thirdpart:$PYTHONPATH
export PYTHONPATH=${INSTALLPATH}/seafile/lib64/python2.7/site-packages:$PYTHONPATH
export PYTHONPATH=${INSTALLPATH}/seahub:$PYTHONPATH
export PYTHONPATH=${INSTALLPATH}/seahub-extra:$PYTHONPATH
export PYTHONPATH=${INSTALLPATH}/pro/python:$PYTHONPATH
export PYTHONPATH="..:${PYTHONPATH}"

OPTS=""
while getopts ":" opt; do
   OPTS="${OPTS}${OPTARG}" 
done

shift $(($OPTIND - 1))

#if [ -n "$OPTS" ]; then
    # always add verbose option
    OPTS="-v${OPTS}"
#fi

pytest $OPTS $*    


