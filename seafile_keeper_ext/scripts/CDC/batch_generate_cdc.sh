#!/bin/bash
SEAFILE_DIR=/opt/seafile
INSTALLPATH=${SEAFILE_DIR}/seafile-server-latest
default_ccnet_conf_dir=${SEAFILE_DIR}/ccnet
central_config_dir=${SEAFILE_DIR}/conf

# INJECT ENV
source "${SEAFILE_DIR}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

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

export PYTHONPATH=${INSTALLPATH}/seafile/lib/python2.6/site-packages:${INSTALLPATH}/seafile/lib64/python2.6/site-packages:${INSTALLPATH}/seafile/lib/python2.7/site-packages:${INSTALLPATH}/seahub/thirdpart:$PYTHONPATH
export PYTHONPATH=${INSTALLPATH}/seafile/lib/python2.7/site-packages:${INSTALLPATH}/seafile/lib64/python2.7/site-packages:$PYTHONPATH
#Vlad: TODO: check security
export PYTHONPATH=${INSTALLPATH}/seahub:$PYTHONPATH

export PYTHON_EGG_CACHE=$SEAFILE_DIR/.cache/Python-Eggs

export PYTHONIOENCODING=utf-8

function usage () {
    echo "Usage: `basename $0`"
    echo "exit."
    exit 1
}
if [ $# != 0 ]; then
    usage
fi

echo_green "CDC generator started at $(date)"
START=$(timestamp)

EXEC_DIR=$(dirname $(readlink -f $0))

pushd $EXEC_DIR
python batch_generate_cdc.py
popd

echo_green "CDC generator ended at $(date)"
echo_green "Elapsed time in seconds: $(($(timestamp) - $START))"


