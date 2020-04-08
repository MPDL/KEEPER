#!/bin/bash

# =================================================================================
# GPFS health monitor plugin for Nagios
#
# Name          : check_gpfs_health.sh
# Type          : Shell Script
# Package               : uadmtools for nagios (ua_monitor)
# Creation date : 13 march 2011
# Platform      : Linux (Red Hat Linux Flavor)
# Created by    : Steve Bosek - steve.bosek@ephris.net - steve.bosek@gmail.com
# Description   : Nagios plugin (script) to GPFS health monitor
#                                       - Check GPFS deamon is active
#                                       - Check GPFS device is healthy
#                                       - Check GPFS Disk are available and up
#                                       - Check GPFS inodes used in percent (you can define warning and critical threshold)
#                                       - Check GPFS MountPoint is healthy (mount and writable)
#                This script has been designed and written on Redhat Linux Plateform
#
#
# Usage         : Add the following line in the /etc/sudoers
#                                 nagios ALL=(ALL) NOPASSWD:path_to_this_script
#
#                                 ./check_gpfs_health.sh -d [device] -m [mounpoint] -o [none|inode] -w [warning_threshold] -c [critical_threshold]
#                                 ./check_gpfs_health.sh -d /dev/DATA -m /gpfs_data -w 80 -c 90
#                                 OK : Daemon mmfsd is active, Device /dev/DATA, Disk(GPFS1 GPFS2 GPFS0 GPFS3 GPFS4 GPFS5 GPFS6 GPFS7),
#                                 Inodes(71.96% used), Mountpoint(/gpfs_data) | /dev/DATA=7000064;1962382;71.96%;80;90
#
#                                 To disable inode control:
#                                 ./check_gpfs_health.sh -d /dev/DATA -m /gpfs_data -x inode
#                                  OK : Daemon mmfsd is active, Device /dev/DATA, Disk(GPFS1 GPFS2 GPFS0 GPFS3 GPFS4 GPFS5 GPFS6 GPFS7),
#                                 Inodes(71.96% used), Mountpoint(/gpfs_data)
#----------------------------------------------------------------------------------
# TODO          : Add Threshold in number used inode
#
#----------------------------------------------------------------------------------
# HISTORY :
#     Release   |   Date        |    Authors            |       Description
# --------------+---------------+-----------------------+-------------------------
# 1.0           | 13.03.2011    | Steve Bosek           | Creation
# 1.1                   | 22.03.2011    | Steve Bosek                   | Bug in $var for default v_warn_inode and v_crit_inode
#                                                                                                               | Perfdata : add used inodes number and uniform
#                                                                                                               | Add a new option (-x inode) to disable inode control: Isn't useful to monitor inode
#                                                                                                               | occupancy rate for a device on all GPFS servers. One is enough per device.
# =================================================================================


# ------------------------------------------------------------------------------
# Debug Mode
# ------------------------------------------------------------------------------
#set -x   # Uncomment to debug this shell script
#set -n   # Uncomment to check command syntax without any execution


# ------------------------------------------------------------------------------
# Nagios Variable Environnement
# ------------------------------------------------------------------------------
# Nagios return codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3


# ------------------------------------------------------------------------------
# Standard Script Info Functions
# ------------------------------------------------------------------------------

# Plugin variable description
PROGNAME=$(basename $0)
PROGPATH=$(echo $0 | sed -e 's,[\\/][^\\/][^\\/]*$,,')
REVISION="Revision 1.1"
AUTHOR="(c) 2011 Steve Bosek (steve.bosek@ephris.net)"

function PrintUsage {
        echo "Usage: $PROGNAME"
        echo "$PROGNAME -d [device] -m [mountpoint] -x [none|noinode] -w warn -c critical"
        echo ""
        echo "  -v Script version"
        echo "  -h Show this page"
        echo "  -d Device path to check"
                echo "  -m Mount path to check"
                echo "  -o Optionnal parameter (default:""). To disable inode controle -x inode"
        echo "  -w Warning threshold for used inodes in % (default: 90)"
        echo "  -c Critical threshold for used inodes in % (default: 95)"
        echo ""
        echo "Usage: $PROGNAME"
        echo "Usage: $PROGNAME --help"
        echo ""
        exit 0
}


function PrintInfo {
        echo "$PROGNAME $REVISION $AUTHOR"
}

function PrintHelp {
        echo ""
        PrintInfo
        echo ""
        PrintUsage
        echo ""
        exit 0
}

# ------------------------------------------------------------------------------
# Default Parameter Value
# ------------------------------------------------------------------------------
v_warn_inode=${v_warn_inode:="90"}
v_crit_inode=${v_crit_inode:="95"}
v_bin_dir=${v_bin_dir:="/usr/lpp/mmfs/bin"}
v_tmp_file="/tmp/workfile$$_gpfs.tmp"
p_mnt_check="/tmp/test_mnt_gpfs.tmp"
v_disable=${v_disable:=""}
msg=""
# Trap
trap 'rm -f "$v_tmp_file" >/dev/null 2>&1' 0
trap "exit 2" 1 2 3 15
# ------------------------------------------------------------------------------
# Grab the command line arguments
# ------------------------------------------------------------------------------

while [ $# -gt 0 ]; do
        case "$1" in
                -h | --help)
                        PrintHelp
                        exit 0;;
                -v | --version)
                        PrintInfo
                        exit 0;;
                -s | --service)
                        shift
                        v_service=$1;;
                -d | --device)
                        shift
                        v_dev=$1;;
                                -m | --mnt)
                        shift
                        v_mnt=$1;;
                -x | --disable | --opt)
                                shift
                                v_disable=$1;;
                -w | --warn)
                        shift
                        v_warn_inode=$1;;
                -c | --crit)
                        shift
                        v_crit_inode=$1;;
                *)  echo "Unknown argument: $1"
                        PrintUsage
                exit 1
                ;;
                esac
        shift
done


if [ "$v_disable" = "inode" ]; then
v_perfdata=""
else
v_perfdata="| device=$v_dev;num_inode=0;free_inode=0;used_inode=0;pused_inode=0%;warn_inode=$v_warn_inode;crit_inode=$v_crit_inode"
fi
# ------------------------------------------------------------------------------
# Script Function
# ------------------------------------------------------------------------------

function f_proc_status {
v_proc_status=`sudo $v_bin_dir/mmgetstate | tail -1 | awk -F " " '{ print $3 }'`
if [ "$v_proc_status" != "active" ]; then
        echo "CRITICAL : Deamon mmfsd not active $v_perfdata"
        exit $STATE_CRITICAL
else
        msg="Daemon mmfsd is active,"
        #exit $STATE_OK
fi
}

function f_disk_status {
if [ "$v_dev" = "" -o "$v_mnt" = "" ]; then
        echo "You must define device and mounpoint"
        exit $STATE_UNKNOWN
fi
# ------------------------------------------------------------------------------
# Check Device
# ------------------------------------------------------------------------------
#local v_dev
#local v_mnt
local v_proc

#v_dev=$1
#v_mnt=$2

$v_bin_dir/mmlsfs $v_dev > /dev/null 2>&1
if [ $? != 0 ]; then
        echo "CRITICAL : A failure has occured on device $v_dev $v_perfdata"
        exit $STATE_CRITICAL
else
        msg="$msg Device $v_dev,"
fi

# ------------------------------------------------------------------------------
# Check Disk
# -----------------------------------------------------------------------------
sudo $v_bin_dir/mmlsdisk $v_dev | sed '1,3d' > $v_tmp_file
while read line ; do
        v_disk_name=`echo $line | awk -F " " '{ print $1 }'`
        v_disk_status=`echo $line | awk -F " " '{ print $7 }'`
        v_disk_available=`echo $line | awk -F " " '{ print $8 }'`
        if [ "$v_disk_status" != "ready" -o "$v_disk_available" != "up" ]; then
                a_disk_fault=( ${a_disk_fault[@]} "$v_disk_name:$v_disk_status and $v_disk_available," )
        else
                a_disk_ok=( ${a_disk_ok[@]} $v_disk_name )
        fi
        done < $v_tmp_file

if [ ${#a_disk_fault[@]} != 0 ]; then
        echo "CRITICAL : Disk failure on ${a_disk_fault[@]} $v_perfdata"
        exit $STATE_CRITICAL
else
        msg="$msg Disk(${a_disk_ok[@]}),"
fi

# ------------------------------------------------------------------------------
# Check Inode
# ------------------------------------------------------------------------------
if [ "$v_disable" != "inode" ]; then
        $v_bin_dir/mmdf $v_dev -F > $v_tmp_file
        num_inode=`grep "number of inodes:" $v_tmp_file | cut -d":" -f2 | sed "s/ //g"`
        free_inode=`grep "free inodes:" $v_tmp_file | cut -d":" -f2 | sed "s/ //g"`
        used_inode=`grep "used inodes:" $v_tmp_file | cut -d":" -f2 | sed "s/ //g"`
        used_pinode=$( echo "scale=2; ($used_inode*100)/$num_inode" | bc )
        if [ "${used_pinode%%.*}" = "" ]; then
                used_pinode=0
        fi
        # Futur threshold in script parameter
        v_perfdata="| device=$v_dev;num_inode=${num_inode};free_inode=$free_inode;used_inode=$used_inode;pused_inode=${used_pinode}%;warn_inode=$v_warn_inode;crit_inode=$v_crit_inode"
        if [ "${used_pinode%%.*}" -ge "$v_crit_inode" ]; then
        echo "CRITICAL : ${used_pinode}% inodes used of ${num_inode} are greater than $v_crit_inode% on $v_dev $v_perfdata"
        exit $STATE_CRITICAL
        elif [ "${used_pinode%%.*}" -ge "$v_warn_inode" ]; then
       echo "WARNING : ${used_pinode}% inodes used of ${num_inode} are greater than $v_warn_inode% on $v_dev $v_perfdata"
       exit $STATE_WARNING
        else
       msg="$msg Inodes(${used_pinode}% used),"
        fi
else
        num_inode="0"
        free_inode="0"
        used_inode="0"
        used_pinode="0"
fi
# ------------------------------------------------------------------------------
# Check Mountpoint
# ------------------------------------------------------------------------------

cat > "${p_mnt_check}" << EOF
#!/bin/sh
cd \$1 || { exit 2; }
exit 0;
EOF

chmod +x ${p_mnt_check}

mount | grep " $v_mnt " > /dev/null
if [ $? != "0" ]; then
                echo "CRITICAL : Mountpoint ${v_mnt} not mounted $v_perfdata"
                exit $STATE_CRITICAL
elif [ `ps -ef | grep "${p_mnt_check}" | grep -v grep | wc -l` -gt 0 ]; then
        echo "CRITICAL : Mountpoint ${v_mnt} is stale $v_perfdata"
else
        ${p_mnt_check} $v_mnt &
        sleep 1
        v_proc=`ps -ef | grep "${p_mnt_check} $v_mnt" | grep -v grep | awk '{print $2}'`
                if [ -n "$v_proc" ]; then
                        kill -9 $v_proc
                                                echo "CRITICAL : Mountpoint ${v_mnt} is stale $v_perfdata"
                                                exit $STATE_CRITICAL
                else
                                                msg="$msg Mountpoint($v_mnt)"
                                                echo "OK : $msg $v_perfdata"
                                                exit $STATE_OK
                fi
        fi
}

f_proc_status
f_disk_status
peterfi@app01-qa-keeper:~$ cat /usr/local/nagios/libexec/check_gpfs_health.sh
#!/bin/bash

# =================================================================================
# GPFS health monitor plugin for Nagios
#
# Name          : check_gpfs_health.sh
# Type          : Shell Script
# Package               : uadmtools for nagios (ua_monitor)
# Creation date : 13 march 2011
# Platform      : Linux (Red Hat Linux Flavor)
# Created by    : Steve Bosek - steve.bosek@ephris.net - steve.bosek@gmail.com
# Description   : Nagios plugin (script) to GPFS health monitor
#                                       - Check GPFS deamon is active
#                                       - Check GPFS device is healthy
#                                       - Check GPFS Disk are available and up
#                                       - Check GPFS inodes used in percent (you can define warning and critical threshold)
#                                       - Check GPFS MountPoint is healthy (mount and writable)
#                This script has been designed and written on Redhat Linux Plateform
#
#
# Usage         : Add the following line in the /etc/sudoers
#                                 nagios ALL=(ALL) NOPASSWD:path_to_this_script
#
#                                 ./check_gpfs_health.sh -d [device] -m [mounpoint] -o [none|inode] -w [warning_threshold] -c [critical_threshold]
#                                 ./check_gpfs_health.sh -d /dev/DATA -m /gpfs_data -w 80 -c 90
#                                 OK : Daemon mmfsd is active, Device /dev/DATA, Disk(GPFS1 GPFS2 GPFS0 GPFS3 GPFS4 GPFS5 GPFS6 GPFS7),
#                                 Inodes(71.96% used), Mountpoint(/gpfs_data) | /dev/DATA=7000064;1962382;71.96%;80;90
#
#                                 To disable inode control:
#                                 ./check_gpfs_health.sh -d /dev/DATA -m /gpfs_data -x inode
#                                  OK : Daemon mmfsd is active, Device /dev/DATA, Disk(GPFS1 GPFS2 GPFS0 GPFS3 GPFS4 GPFS5 GPFS6 GPFS7),
#                                 Inodes(71.96% used), Mountpoint(/gpfs_data)
#----------------------------------------------------------------------------------
# TODO          : Add Threshold in number used inode
#
#----------------------------------------------------------------------------------
# HISTORY :
#     Release   |   Date        |    Authors            |       Description
# --------------+---------------+-----------------------+-------------------------
# 1.0           | 13.03.2011    | Steve Bosek           | Creation
# 1.1                   | 22.03.2011    | Steve Bosek                   | Bug in $var for default v_warn_inode and v_crit_inode
#                                                                                                               | Perfdata : add used inodes number and uniform
#                                                                                                               | Add a new option (-x inode) to disable inode control: Isn't useful to monitor inode
#                                                                                                               | occupancy rate for a device on all GPFS servers. One is enough per device.
# =================================================================================


# ------------------------------------------------------------------------------
# Debug Mode
# ------------------------------------------------------------------------------
#set -x   # Uncomment to debug this shell script
#set -n   # Uncomment to check command syntax without any execution


# ------------------------------------------------------------------------------
# Nagios Variable Environnement
# ------------------------------------------------------------------------------
# Nagios return codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3


# ------------------------------------------------------------------------------
# Standard Script Info Functions
# ------------------------------------------------------------------------------

# Plugin variable description
PROGNAME=$(basename $0)
PROGPATH=$(echo $0 | sed -e 's,[\\/][^\\/][^\\/]*$,,')
REVISION="Revision 1.1"
AUTHOR="(c) 2011 Steve Bosek (steve.bosek@ephris.net)"

function PrintUsage {
        echo "Usage: $PROGNAME"
        echo "$PROGNAME -d [device] -m [mountpoint] -x [none|noinode] -w warn -c critical"
        echo ""
        echo "  -v Script version"
        echo "  -h Show this page"
        echo "  -d Device path to check"
                echo "  -m Mount path to check"
                echo "  -o Optionnal parameter (default:""). To disable inode controle -x inode"
        echo "  -w Warning threshold for used inodes in % (default: 90)"
        echo "  -c Critical threshold for used inodes in % (default: 95)"
        echo ""
        echo "Usage: $PROGNAME"
        echo "Usage: $PROGNAME --help"
        echo ""
        exit 0
}


function PrintInfo {
        echo "$PROGNAME $REVISION $AUTHOR"
}

function PrintHelp {
        echo ""
        PrintInfo
        echo ""
        PrintUsage
        echo ""
        exit 0
}

# ------------------------------------------------------------------------------
# Default Parameter Value
# ------------------------------------------------------------------------------
v_warn_inode=${v_warn_inode:="90"}
v_crit_inode=${v_crit_inode:="95"}
v_bin_dir=${v_bin_dir:="/usr/lpp/mmfs/bin"}
v_tmp_file="/tmp/workfile$$_gpfs.tmp"
p_mnt_check="/tmp/test_mnt_gpfs.tmp"
v_disable=${v_disable:=""}
msg=""
# Trap
trap 'rm -f "$v_tmp_file" >/dev/null 2>&1' 0
trap "exit 2" 1 2 3 15
# ------------------------------------------------------------------------------
# Grab the command line arguments
# ------------------------------------------------------------------------------

while [ $# -gt 0 ]; do
        case "$1" in
                -h | --help)
                        PrintHelp
                        exit 0;;
                -v | --version)
                        PrintInfo
                        exit 0;;
                -s | --service)
                        shift
                        v_service=$1;;
                -d | --device)
                        shift
                        v_dev=$1;;
                                -m | --mnt)
                        shift
                        v_mnt=$1;;
                -x | --disable | --opt)
                                shift
                                v_disable=$1;;
                -w | --warn)
                        shift
                        v_warn_inode=$1;;
                -c | --crit)
                        shift
                        v_crit_inode=$1;;
                *)  echo "Unknown argument: $1"
                        PrintUsage
                exit 1
                ;;
                esac
        shift
done


if [ "$v_disable" = "inode" ]; then
v_perfdata=""
else
v_perfdata="| device=$v_dev;num_inode=0;free_inode=0;used_inode=0;pused_inode=0%;warn_inode=$v_warn_inode;crit_inode=$v_crit_inode"
fi
# ------------------------------------------------------------------------------
# Script Function
# ------------------------------------------------------------------------------

function f_proc_status {
v_proc_status=`sudo $v_bin_dir/mmgetstate | tail -1 | awk -F " " '{ print $3 }'`
if [ "$v_proc_status" != "active" ]; then
        echo "CRITICAL : Deamon mmfsd not active $v_perfdata"
        exit $STATE_CRITICAL
else
        msg="Daemon mmfsd is active,"
        #exit $STATE_OK
fi
}

function f_disk_status {
if [ "$v_dev" = "" -o "$v_mnt" = "" ]; then
        echo "You must define device and mounpoint"
        exit $STATE_UNKNOWN
fi
# ------------------------------------------------------------------------------
# Check Device
# ------------------------------------------------------------------------------
#local v_dev
#local v_mnt
local v_proc

#v_dev=$1
#v_mnt=$2

$v_bin_dir/mmlsfs $v_dev > /dev/null 2>&1
if [ $? != 0 ]; then
        echo "CRITICAL : A failure has occured on device $v_dev $v_perfdata"
        exit $STATE_CRITICAL
else
        msg="$msg Device $v_dev,"
fi

# ------------------------------------------------------------------------------
# Check Disk
# -----------------------------------------------------------------------------
sudo $v_bin_dir/mmlsdisk $v_dev | sed '1,3d' > $v_tmp_file
while read line ; do
        v_disk_name=`echo $line | awk -F " " '{ print $1 }'`
        v_disk_status=`echo $line | awk -F " " '{ print $7 }'`
        v_disk_available=`echo $line | awk -F " " '{ print $8 }'`
        if [ "$v_disk_status" != "ready" -o "$v_disk_available" != "up" ]; then
                a_disk_fault=( ${a_disk_fault[@]} "$v_disk_name:$v_disk_status and $v_disk_available," )
        else
                a_disk_ok=( ${a_disk_ok[@]} $v_disk_name )
        fi
        done < $v_tmp_file

if [ ${#a_disk_fault[@]} != 0 ]; then
        echo "CRITICAL : Disk failure on ${a_disk_fault[@]} $v_perfdata"
        exit $STATE_CRITICAL
else
        msg="$msg Disk(${a_disk_ok[@]}),"
fi

# ------------------------------------------------------------------------------
# Check Inode
# ------------------------------------------------------------------------------
if [ "$v_disable" != "inode" ]; then
        $v_bin_dir/mmdf $v_dev -F > $v_tmp_file
        num_inode=`grep "number of inodes:" $v_tmp_file | cut -d":" -f2 | sed "s/ //g"`
        free_inode=`grep "free inodes:" $v_tmp_file | cut -d":" -f2 | sed "s/ //g"`
        used_inode=`grep "used inodes:" $v_tmp_file | cut -d":" -f2 | sed "s/ //g"`
        used_pinode=$( echo "scale=2; ($used_inode*100)/$num_inode" | bc )
        if [ "${used_pinode%%.*}" = "" ]; then
                used_pinode=0
        fi
        # Futur threshold in script parameter
        v_perfdata="| device=$v_dev;num_inode=${num_inode};free_inode=$free_inode;used_inode=$used_inode;pused_inode=${used_pinode}%;warn_inode=$v_warn_inode;crit_inode=$v_crit_inode"
        if [ "${used_pinode%%.*}" -ge "$v_crit_inode" ]; then
        echo "CRITICAL : ${used_pinode}% inodes used of ${num_inode} are greater than $v_crit_inode% on $v_dev $v_perfdata"
        exit $STATE_CRITICAL
        elif [ "${used_pinode%%.*}" -ge "$v_warn_inode" ]; then
       echo "WARNING : ${used_pinode}% inodes used of ${num_inode} are greater than $v_warn_inode% on $v_dev $v_perfdata"
       exit $STATE_WARNING
        else
       msg="$msg Inodes(${used_pinode}% used),"
        fi
else
        num_inode="0"
        free_inode="0"
        used_inode="0"
        used_pinode="0"
fi
# ------------------------------------------------------------------------------
# Check Mountpoint
# ------------------------------------------------------------------------------

cat > "${p_mnt_check}" << EOF
#!/bin/sh
cd \$1 || { exit 2; }
exit 0;
EOF

chmod +x ${p_mnt_check}

mount | grep " $v_mnt " > /dev/null
if [ $? != "0" ]; then
                echo "CRITICAL : Mountpoint ${v_mnt} not mounted $v_perfdata"
                exit $STATE_CRITICAL
elif [ `ps -ef | grep "${p_mnt_check}" | grep -v grep | wc -l` -gt 0 ]; then
        echo "CRITICAL : Mountpoint ${v_mnt} is stale $v_perfdata"
else
        ${p_mnt_check} $v_mnt &
        sleep 1
        v_proc=`ps -ef | grep "${p_mnt_check} $v_mnt" | grep -v grep | awk '{print $2}'`
                if [ -n "$v_proc" ]; then
                        kill -9 $v_proc
                                                echo "CRITICAL : Mountpoint ${v_mnt} is stale $v_perfdata"
                                                exit $STATE_CRITICAL
                else
                                                msg="$msg Mountpoint($v_mnt)"
                                                echo "OK : $msg $v_perfdata"
                                                exit $STATE_OK
                fi
        fi
}

f_proc_status
f_disk_status
