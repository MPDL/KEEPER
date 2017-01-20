#!/bin/bash

# icinga check script for KEEPER non handled viruses
# to be copied to /usr/local/nagios/libexec

# See https://github.com/MPDL/KEEPER/issues/26

RESULTS=$(/opt/seafile/scripts/run_keeper_script.sh /opt/seafile/scripts/monitoring/viruses_status.py)
RC=$?

echo -e "$RESULTS"

exit $RC 
