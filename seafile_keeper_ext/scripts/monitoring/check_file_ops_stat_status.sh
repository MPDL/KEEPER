#!/bin/bash

# icinga check script for KEEPER libevent propagation problem
# to be linked from /usr/local/nagios/libexec

RESULTS=$(/opt/seafile/scripts/run_keeper_script.sh /opt/seafile/scripts/monitoring/file_ops_stat_status.py)
RC=$?

echo -e "$RESULTS"

exit $RC 
