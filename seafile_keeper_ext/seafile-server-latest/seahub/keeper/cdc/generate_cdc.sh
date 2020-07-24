#!/bin/bash
SEAFILE_DIR=${__SEAFILE_DIR__}
INSTALLPATH=${SEAFILE_DIR}/seafile-server-latest
default_ccnet_conf_dir=${SEAFILE_DIR}/ccnet
central_config_dir=${SEAFILE_DIR}/conf
seafile_data_dir=${SEAFILE_DIR}/seafile-data
pro_pylibs_dir=${INSTALLPATH}/pro/python

# INJECT ENV
source "${SEAFILE_DIR}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

export CCNET_CONF_DIR=${default_ccnet_conf_dir}
export SEAFILE_CONF_DIR=${seafile_data_dir}
export SEAFILE_CENTRAL_CONF_DIR=${central_config_dir}
export SEAFES_DIR=$pro_pylibs_dir/seafes

export PYTHONPATH=${INSTALLPATH}/seafile/lib/python3.6/site-packages:${INSTALLPATH}/seafile/lib64/python3.6/site-packages:${INSTALLPATH}/seahub/thirdpart:$PYTHONPATH
export PYTHONPATH=$PYTHONPATH:${INSTALLPATH}/seahub/
#export PYTHONPATH=$PYTHONPATH:$pro_pylibs_dir
#export PYTHONPATH=$PYTHONPATH:${INSTALLPATH}/seahub-extra/
#export PYTHONPATH=$PYTHONPATH:${INSTALLPATH}/seahub-extra/thirdparts

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
python generate_cdc.py
popd

echo_green "CDC generator ended at $(date)"
echo_green "Elapsed time in seconds: $(($(timestamp) - $START))"


