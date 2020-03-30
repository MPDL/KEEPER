#!/bin/bash
SEAFILE_DIR=__SEAFILE_DIR__
INSTALLPATH=${SEAFILE_DIR}/seafile-server-latest
default_ccnet_conf_dir=${SEAFILE_DIR}/ccnet
central_config_dir=${SEAFILE_DIR}/conf
default_seafile_data_dir=${SEAFILE_DIR}/seafile-data
seafile_rpc_pipe_path=${INSTALLPATH}/runtime

# INJECT ENV
source "${SEAFILE_DIR}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

export CCNET_CONF_DIR=${default_ccnet_conf_dir}
export SEAFILE_CONF_DIR=${default_seafile_data_dir}
export SEAFILE_CENTRAL_CONF_DIR=${central_config_dir}
export SEAFES_DIR=${INSTALLPATH}/pro/python/seafes
export SEAHUB_DIR=${INSTALLPATH}/seahub
export SEAHUB_LOG_DIR=${SEAFILE_DIR}/logs
export SEAFILE_RPC_PIPE_PATH=${seafile_rpc_pipe_path}

export PYTHONPATH=${INSTALLPATH}/seafile/lib/python3.6/site-packages:${INSTALLPATH}/seahub/thirdpart:$PYTHONPATH
#Vlad: TODO: check security
export PYTHONPATH=${INSTALLPATH}/seahub:$PYTHONPATH
export PYTHONPATH=${INSTALLPATH}/seahub-extra:$PYTHONPATH
export PYTHONPATH=${INSTALLPATH}/pro/python:$PYTHONPATH

#export PYTHON_EGG_CACHE=$SEAFILE_DIR/.cache/Python-Eggs

export PYTHONIOENCODING=utf-8

#echo $PYTHONPATH

python $*  



