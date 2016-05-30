#!/bin/bash

GPFS_DEVICE="gpfs_keeper"
GPFS_SNAPSHOT="mmbackupSnap"

PATH=$PATH:/usr/lpp/mmfs/bin
export PATH


### EXECUTE ON SEAFILE SERVER - lta01 ###

# 0. Check for old snapshot
# If there is one, the last backup didn't finish -> something is wrong
mmlssnapshot $GPFS_DEVICE -s $GPFS_SNAPSHOT 2>&1 > /dev/null
if [ $? = 0 ]
then
	# Old snapshot still exists, something is wrong
	# TODO: alert
	exit 1
fi

# 1. Shut down seafile / nginx and dump database
# TODO

# 2. Create filesystem snapshot
mmcrsnapshot $GPFS_DEVICE $GPFS_SNAPSHOT
if [ $? -ne 0 ]
then
	# Could not create snapshot, something is wrong
	# TODO: alert
	exit 1
fi

# (3. TSM-Agent on lta03 will backup snapshot data asynchronously and delete snapshot after it is finished)

# 4. Start seafile / nginx again
# TODO
