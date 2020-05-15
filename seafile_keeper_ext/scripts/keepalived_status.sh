#!/bin/bash

TYPE=$1
NAME=$2
STATE=$3

case $STATE in
        "MASTER") echo $1 $2 is in $3 state > /var/run/keepalived.state
                  exit 0
                  ;;
        "BACKUP") echo $1 $2 is in $3 state > /var/run/keepalived.state
                  exit 0
                  ;;
        "FAULT")  echo $1 $2 is in $3 state > /var/run/keepalived.state
                  exit 0
                  ;;
        *)        echo "unknown state"
                  exit 1
                  ;;
esac
