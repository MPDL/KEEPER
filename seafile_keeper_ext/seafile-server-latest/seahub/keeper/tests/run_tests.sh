#!/bin/bash

SEAFILE_DIR=__SEAFILE_DIR__
INSTALLPATH=${SEAFILE_DIR}/seafile-server-latest
default_ccnet_conf_dir=${SEAFILE_DIR}/ccnet
central_config_dir=${SEAFILE_DIR}/conf
seafile_data_dir=${SEAFILE_DIR}/seafile-data
#get path of seafile.conf
seafile_rpc_pipe_path=${INSTALLPATH}/runtime

export CCNET_CONF_DIR=${default_ccnet_conf_dir}
export SEAFILE_CONF_DIR=${seafile_data_dir}
export SEAFILE_CENTRAL_CONF_DIR=${central_config_dir}
export SEAFES_DIR=${INSTALLPATH}/pro/python/seafes
export SEAHUB_LOG_DIR=${SEAFILE_DIR}/logs
export SEAFILE_RPC_PIPE_PATH=${seafile_rpc_pipe_path}

export DJANGO_SETTINGS_MODULE=seahub.settings

export PYTHONPATH=${INSTALLPATH}/seahub/thirdpart:$PYTHONPATH
export PYTHONPATH=${INSTALLPATH}/seafile/lib/python3.6/site-packages:$PYTHONPATH
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


