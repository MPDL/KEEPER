#!/bin/bash

### EXECUTE ON BACKUP SERVER - lta03 ###

TODAY=`date '+%Y%m%d'`
WEEKDAY=`date '+%u'`

GPFS_DEVICE="gpfs_keeper"
GPFS_SNAPSHOT="mmbackupSnap"

#TODO: Rotate snapshots to deal with backups taking >24 hours using something like
#GPFS_SNAPSHOT="mmbackupSnap$TODAY"

PATH=$PATH:/usr/lpp/mmfs/bin
export PATH

DSM_CONFIG_DIR=/opt/tivoli/tsm/client/ba/bin
DSM_CONFIG=$DSM_CONFIG_DIR/dsm.opt
export DSM_CONFIG

DSM_LOG=/var/log/mmbackup
export DSM_LOG

MMBACKUP_PROGRESS_CONTENT=0x07
export MMBACKUP_PROGRESS_CONTENT


mmlssnapshot $GPFS_DEVICE -s $GPFS_SNAPSHOT
if [ $? -ne 0 ]
then
	# No snapshot, application backup probably didn't run
	echo "Cannot find snapshot $GPFS_SNAPSHOT for filesystem $GPFS_DEVICE"
	exit 1
fi


# Full backup the first time:
# mmbackup /dev/$GPFS_DEVICE --noquote -s /var/tmp -v -t full -B 1000 -L 6 -m 8 -S $GPFS_SNAPSHOT

if [ "$WEEKDAY" = 7 ]
then
	# Rebuild the shadow database on Sundays
	mmbackup /dev/$GPFS_DEVICE --noquote -s /var/tmp -v -q -t incremental -B 1000 -L 6 -m 8 -S $GPFS_SNAPSHOT
else
	# Normal incremental backup on other days
	mmbackup /dev/$GPFS_DEVICE --noquote -s /var/tmp -v -t incremental -B 1000 -L 6 -m 8 -S $GPFS_SNAPSHOT
fi

mmdelsnapshot $GPFS_DEVICE $GPFS_SNAPSHOT

exit

