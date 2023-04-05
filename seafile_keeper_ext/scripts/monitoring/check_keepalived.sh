#!/bin/bash

###############################################################
#       Check Keepalived State                                #
#                                                             #
#       Author:         Zhivko Todorov <ztodorov@neterra.net> #
#       Date:           01-Dec-2015                           #
#       Version:        0.0.1                                 #
#       License:        GPL                                   #
###############################################################


# set to 'true' if the host is supposed to be in MASTER state
# or set to 'false' if the host is supposed to be in BACKUP state
# nrpe cannot receive external variables UNLESS is forced in config
MASTER='true'

# checking if there are alive keepalived processes so we can trust the content of the notify 'state' file
KEEPALIVENUM=`ps uax|grep '/usr/sbin/keepalived'|grep -v grep|wc -l`

if [ "$KEEPALIVENUM" -gt 0 ]; then

  KEEPALIVESTATE=`cat /var/run/keepalived.state`

  if [ "$MASTER" == "true" ]; then

    if [[ $KEEPALIVESTATE == *"MASTER"* ]];then
      echo $KEEPALIVESTATE
      exit 0
    fi

    if [[ $KEEPALIVESTATE == *"BACKUP"* ]];then
      echo $KEEPALIVESTATE
      exit 2
    fi

  else

    if [[ $KEEPALIVESTATE == *"BACKUP"* ]];then
      echo $KEEPALIVESTATE
      exit 0
    fi

    if [[ $KEEPALIVESTATE == *"MASTER"* ]];then
      echo $KEEPALIVESTATE
      exit 2
    fi

  fi
fi

echo "Keepalived is in UNKNOWN state"
exit 3

