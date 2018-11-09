#!/bin/bash

### KEEPER COMMON Utils

function echo_green () {
    if [ "$(tput colors 2>/dev/null)" ]; then 
        echo -e "$(tput setaf 2)${1}$(tput sgr0)"
    else
        echo -e "${1}"
    fi
}

function echo_red () {
    if [ "$(tput colors 2>/dev/null)" ]; then 
        echo -e "$(tput setaf 1)${1}$(tput sgr0)"
    else
        echo -e "${1}"
    fi
}

function err_and_exit () {
	if [ "$1" ]; then
        echo_red "Error: $1"
		# TODO: send notification 
	fi
	exit 1;
}

function warn () {
	if [ "$1" ]; then
        echo_red "Warning: $1"
		# TODO: send notification 
	fi
}

function check_file () {
    if [ ! -f "$1" ]; then
		if [ -n "$2" ]; then
			err_and_exit "$2"
		fi
        err_and_exit "Cannot find file $1"
    fi
}

function timestamp () {
    echo $(date +'%s')
}

# calculate elapsed time, 
# first param is start timestamp in seconds
function elapsed_time() {
    ELAPSED_TIME=$(($(timestamp) - ${1}))
    printf '%dh:%dm:%ds' $((${ELAPSED_TIME}/3600)) $((${ELAPSED_TIME}%3600/60)) $((${ELAPSED_TIME}%60))
}

### INJECT KEEPER PROPERTIES

PROPS_DIR=$(dirname $(dirname $(readlink -f $0)))

### GET INSTANCE PROPERTIES FILE
# KEEPER instance properties file should be located in PROPS_DIR!!!
FILES=( $(find ${PROPS_DIR} -maxdepth 1 -type f -name "keeper*.ini") )
( [[ $? -ne 0 ]] || [[ ${#FILES[@]} -eq 0 ]] ) && err_and_exit "Cannot find instance properties file in ${PROPS_DIR}"
[[ ${#FILES[@]} -ne 1 ]] && err_and_exit "Too many instance properties files in ${PROPS_DIR}:\n ${FILES[*]}"
PROPERTIES_FILE="${FILES[0]}"
source <(grep -v "^[[#;]" ${PROPERTIES_FILE})
#source 1.txt
if [ $? -ne 0  ]; then
	err_and_exit "Cannot intitialize variables"
fi

SEAFILE_DIR=${__SEAFILE_DIR__}
SEAFILE_LATEST_DIR=${SEAFILE_DIR}/seafile-server-latest
### END


