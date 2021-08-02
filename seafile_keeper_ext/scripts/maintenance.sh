#!/bin/bash

if [ $# -lt 1 ]
then
        echo "Usage: $0 <check|start>"
        exit
fi

CURR_DIR=$(dirname $(readlink -f $0))
source "${CURR_DIR}/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
        echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

MARIADB=0
KERNEL=0

check() {
	if [ ${__NODE_TYPE__} == "APP" ]; then
		apt-mark unhold galera-4 libmariadb3 mysql-common mariadb-common mariadb-backup 2>&1 > /dev/null
        	apt-mark unhold libmysqlclient18 mariadb-client mariadb-client-10.4 mariadb-client-core-10.4 2>&1 > /dev/null
        	apt-mark unhold mariadb-server mariadb-server-10.4 mariadb-server-core-10.4 2>&1 > /dev/null
	fi

	apt-mark unhold linux-headers-* linux-image-* linux-modules-* linux-modules-extra-* 2>&1 > /dev/null

	apt-get update 2>&1 > /dev/null

	if [ ${__NODE_TYPE__} == "APP" ]; then
	        if [ "`apt-cache policy galera-4 | grep Installed | awk '{print $2}'`" != "`apt-cache policy galera-4 | grep Candidate | awk '{print $2}'`" ] || [ "`apt-cache policy mariadb-server-10.4 | grep Installed | awk '{print $2}'`" != "`apt-cache policy mariadb-server-10.4 | grep Candidate | awk '{print $2}'`" ]
        	then
               		MARIADB=1
                	echo "Maintenance will upgrade MariaDB. Seafile and MariaDB will be shutdown temporarily"
        	fi
	fi

	if [ "`apt-cache policy linux-image-generic | grep Installed | awk '{print $2}'`" != "`apt-cache policy linux-image-generic | grep Candidate | awk '{print $2}'`" ]
        then
                KERNEL=1
                echo "Maintenance will upgrade the kernel. A system reboot will be performed."
        fi

        if [ ${__NODE_TYPE__} == "APP" ]; then
                apt-mark hold galera-4 libmariadb3 mysql-common mariadb-common mariadb-backup 2>&1 > /dev/null
                apt-mark hold libmysqlclient18 mariadb-client mariadb-client-10.4 mariadb-client-core-10.4 2>&1 > /dev/null
                apt-mark hold mariadb-server mariadb-server-10.4 mariadb-server-core-10.4 2>&1 > /dev/null
        fi

	apt-mark hold linux-headers-* linux-image-* linux-modules-* linux-modules-extra-* 2>&1 > /dev/null
}

case $1 in
        check)
                check
                ;;
        start)
                check

	        if [ ${__NODE_TYPE__} == "APP" ]; then
	                if [ $MARIADB -eq 1 ]; then
	                        systemctl stop keeper
	                        systemctl stop mariadb
	                fi
			
	                apt-mark unhold galera-4 libmariadb3 mysql-common mariadb-common mariadb-backup 2>&1 > /dev/null
	                apt-mark unhold libmysqlclient18 mariadb-client mariadb-client-10.4 mariadb-client-core-10.4 2>&1 > /dev/null
	                apt-mark unhold mariadb-server mariadb-server-10.4 mariadb-server-core-10.4 2>&1 > /dev/null
	        fi

		apt-mark unhold linux-headers-* linux-image-* linux-modules-* linux-modules-extra-* 2>&1 > /dev/null

                apt-get -y dist-upgrade
                apt-get -y autoremove


                apt-mark hold linux-headers-* linux-image-* linux-modules-* linux-modules-extra-* 2>&1 > /dev/null

		if [ ${__NODE_TYPE__} == "APP" ]; then
	                apt-mark hold galera-4 libmariadb3 mysql-common mariadb-common mariadb-backup 2>&1 > /dev/null
	                apt-mark hold libmysqlclient18 mariadb-client mariadb-client-10.4 mariadb-client-core-10.4 2>&1 > /dev/null
	                apt-mark hold mariadb-server mariadb-server-10.4 mariadb-server-core-10.4 2>&1 > /dev/null

			if [ $MARIADB -eq 1 ]; then
	                        sed -i s/"PermissionsStartOnly=true"/"PermissionsStartOnly=true\n\n\nExecStartPre=\/bin\/bash -c 'while [ ! -d \/keeper\/mysql\/logs ]; do sleep 1; done'\n"/ /lib/systemd/system/mariadb.service
	                        systemctl daemon-reload
				if [ $KERNEL -eq 0 ]; then
		                        systemctl start mariadb
		                        systemctl start keeper
				fi
	                fi
		fi

                if [ $KERNEL -eq 1 ]; then
                        reboot
                fi
                ;;
        *)
                echo "Usage: $0 <check|start>"
                ;;
esac

