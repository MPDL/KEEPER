PATH=$PATH:/afs/ipp/@sys/bin:/usr/lpp/mmfs/bin
export PATH

LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/tivoli/tsm/client/ba/bin
export LD_LIBRARY_PATH

DSM_CONFIG_DIR=/opt/tivoli/tsm/client/ba/bin
DSM_CONFIG=$DSM_CONFIG_DIR/dsm.opt
export DSM_CONFIG

DSM_LOG=/var/log/mmbackup
export DSM_LOG

MMBACKUP_PROGRESS_CONTENT=0x07
export MMBACKUP_PROGRESS_CONTENT

#touch /tmp/dsm.sys
#/bin/cp -p $DSM_CONFIG_DIR/dsm_base.sys $DSM_CONFIG_DIR/dsm.sys

##################################################################
#
# For mmbackups with snapshots:
#

# mmbackup of GPFS Filesystem 'gpfs_keeper', mount point: '/keeper'

WEEKDAY=`date '+%u'`

# snapshot as parameter 

if [ -z "$1" ] 
then 
	echo "Snapshot is not passed as parameter"
	exit 1
else
    	SNAPSHOT=$1 
fi  

mmlssnapshot gpfs_keeper | grep $SNAPSHOT
if [ $? = 0 ]
then

  # Full backup the first time:
#  mmbackup /dev/gpfs_keeper --noquote -s /var/tmp -v -t full -B 1000 -L 6 -m 8 -S $SNAPSHOT

  if [ "$WEEKDAY" = 7 ]
  then
    # Rebuild the shadow database on Sundays
    mmbackup /dev/gpfs_keeper --noquote -s /var/tmp -v -q -t incremental -B 1000 -L 6 -m 8 -S $SNAPSHOT
  else
    # Normal incremental backup on other days
    mmbackup /dev/gpfs_keeper --noquote -s /var/tmp -v -t incremental -B 1000 -L 6 -m 8 -S $SNAPSHOT
  fi

  mmdelsnapshot gpfs_keeper $SNAPSHOT
else
  echo "Cannot find snapshot $SNAPSHOT for filesystem 'gpfs_keeper'"
fi

exit

