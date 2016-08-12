#!/bin/bash
set -x

PATH=$PATH:/afs/ipp/@sys/bin:/usr/lpp/mmfs/bin
export PATH

#LD_LIBRARY_PATH=/usr/lib:/usr/lib64:/opt/tivoli/tsm/client/ba/bin
#export LD_LIBRARY_PATH

DSM_CONFIG_DIR=/opt/tivoli/tsm/client/ba/bin
DSM_CONFIG=$DSM_CONFIG_DIR/dsm.opt
export DSM_CONFIG

DSM_LOG=/var/log/mmbackup
export DSM_LOG

MMBACKUP_PROGRESS_CONTENT=0x07
export MMBACKUP_PROGRESS_CONTENT

### Very verbose backup
#DEBUGmmbackup=0x07
#export DEBUGmmbackup

WEEKDAY=`date '+%u'`

FILESET="seafile-fileset"
LINK="/keeper/${FILESET}"

GPFS_DEVICE="/dev/gpfs_keeper"

#### THE SCRIPT SHOULD BE CALLED WITH SNAPSHOT NAME AS PARAMETER
if [ -z "$1" ]
then
        echo "Snapshot is not passed as parameter"
        exit 1
else
        SNAPSHOT=$1
fi


##################################################################
function fileset_backup () {
  local FILESET=$1
  local LINK=$2
  local SNAPSHOT=$3

#### SNAPSHOT SHOULD BE ALREADY CREATED
  mmlssnapshot $GPFS_DEVICE -j $FILESET | grep $SNAPSHOT
  if [ $? = 0 ]
  then

    # Full backup the first time:
#    mmbackup $LINK --scope inodespace --noquote -s /var/tmp -v -t full -B 1000 -L 6 -m 8 -S $SNAPSHOT 

    if [ "$WEEKDAY" = 7 ]
    then
      # Rebuild the shadow database on Sundays
      mmbackup $LINK --scope inodespace --noquote -s /var/tmp -v -q -t incremental -B 1000 -L 6 -m 8 -a 1 -S $SNAPSHOT
    else
      # Normal incremental backup on other days
      mmbackup $LINK --scope inodespace --noquote -s /var/tmp -v -t incremental -B 1000 -L 6 -m 8 -a 1 -S $SNAPSHOT 
    fi

    mmdelsnapshot $GPFS_DEVICE $SNAPSHOT -j $FILESET
    
  else
    echo "Cannot find snapshot $SNAPSHOT for filesystem 'gpfs_keeper', fileset $FILESET"
    exit 1  
  fi
}
##################################################################

fileset_backup "$FILESET" "$LINK" "$SNAPSHOT"

exit 0

#test
#TODAY=`date '+%u'`
#SNAPSHOT="mmbackupSnap${TODAY}-${FILESET}"
#mmcrsnapshot gpfs_keeper $SNAPSHOT -j $FILESET 
#fileset_backup "$FILESET" "/keeper/${FILESET}" "$SNAPSHOT"

#fileset_backup seafile-fileset /keeper/seafile-fileset
#fileset_backup fs1 /keeper/fs1

