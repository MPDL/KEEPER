#!/bin/bash

### BEGIN INIT INFO
# Provides:          seafile-server
# Required-Start:    $local_fs $remote_fs $network
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Starts Seafile Server
# Description:       starts Seafile Server
### END INIT INFO

set -x

# Change the value of "user" to linux user name who runs seafile
user=root

# Change the value of "seafile_dir" to your path of seafile installation
# usually the home directory of $user
seafile_dir=/opt/seafile
script_path=${seafile_dir}/seafile-server-latest
seafile_init_log=${seafile_dir}/logs/seafile.init.log
seahub_init_log=${seafile_dir}/logs/seahub.init.log
default_ccnet_conf_dir=${seafile_dir}/ccnet

# Change the value of fastcgi to true if fastcgi is to be used
fastcgi=true
# Set the port of fastcgi, default is 8000. Change it if you need different.
fastcgi_port=8001

function check_component_running() {
    name=$1
    cmd=$2
    if pid=$(pgrep -f "$cmd" 2>/dev/null); then
        echo "[$name] is running, pid $pid"
	else
        echo "[$name] is not running"
    fi
}

#
# Write a polite log message with date and time
#
echo -e "\n \n About to perform $1 for seafile at `date -Iseconds` \n " >> ${seafile_init_log}
echo -e "\n \n About to perform $1 for seahub at `date -Iseconds` \n " >> ${seahub_init_log}

case "$1" in
        start|restart)
                sudo -u ${user} ${script_path}/seafile.sh ${1} >> ${seafile_init_log}
                if [ $fastcgi = true ];
                then
                        sudo -u ${user} ${script_path}/seahub.sh ${1}-fastcgi ${fastcgi_port} >> ${seahub_init_log}
                else
                        sudo -u ${user} ${script_path}/seahub.sh ${1} >> ${seahub_init_log}
                fi
                service nginx ${1}
        ;;
#        restart)
#                sudo -u ${user} ${script_path}/seafile.sh ${1} >> ${seafile_init_log}
#                if [ $fastcgi = true ];
#                then
#                        sudo -u ${user} ${script_path}/seahub.sh ${1}-fastcgi ${fastcgi_port} >> ${seahub_init_log}
#                else
#                        sudo -u ${user} ${script_path}/seahub.sh ${1} >> ${seahub_init_log}
#                fi
#        ;;
        stop)
                sudo -u ${user} ${script_path}/seahub.sh ${1} >> ${seahub_init_log}
                sudo -u ${user} ${script_path}/seafile.sh ${1} >> ${seafile_init_log}
        ;;
        status)
			RC=0
			if pid=$(pgrep -f "seafile-controller -c ${default_ccnet_conf_dir}" 2>/dev/null); then
				echo "Seafile controller is running, pid $pid"
			else
				echo "Seafile controller is not running."
				RC=1	
			fi
			check_component_running "ccnet-server" "ccnet-server.*-c ${default_ccnet_conf_dir}"
			check_component_running "seaf-server" "seaf-server.*-c ${default_ccnet_conf_dir}"
			# TODO: check fileserver process: probably it is an old stuff, seaf-server makes the job
            #			check_component_running "fileserver" "fileserver.*-c ${default_ccnet_conf_dir}"
			check_component_running "seafdav" "wsgidav.server.run_server"
			check_component_running "seafevents" "seafevents.main"
			echo "Status is OK"
			exit $RC
        ;;
        *)
                echo "Usage: /etc/init.d/seafile-server {start|stop|restart|status}"
                exit 1
        ;;
esac

