#!/bin/bash
read -p "Please enter the memcached IP [127.0.0.1]: " memcached_host

if [ "$memcached_host" == "" ]
then
  memcached_host='127.0.0.1'
fi

cp -rf src/* /
cat src/opt/seafile/scripts/keeper-oos-log.sh | sed s/__MEMCACHED_HOST__/$memcached_host/g > /opt/seafile/scripts/keeper-oos-log.sh
systemctl daemon-reload
systemctl restart rsyslog
systemctl restart systemd-journald
systemctl restart memcached
systemctl enable keeper-oos-log
systemctl start keeper-oos-log
