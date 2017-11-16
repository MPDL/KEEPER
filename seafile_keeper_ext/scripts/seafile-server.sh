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

#set -x

# Change the value of "user" to linux user name who runs seafile
user=seafile

# Change the value of "seafile_dir" to your path of seafile installation
# usually the home directory of $user
seafile_dir=/opt/seafile
script_path=${seafile_dir}/seafile-server-latest
seafile_init_log=${seafile_dir}/logs/seafile.init.log
seahub_init_log=${seafile_dir}/logs/seahub.init.log
default_ccnet_conf_dir=${seafile_dir}/ccnet

# Change the value of fastcgi to true if fastcgi is to be used
fastcgi=false
# Set the port of fastcgi, default is 8000. Change it if you need different.
fastcgi_port=8001

source "${seafile_dir}/scripts/inject_keeper_env.sh"
if [ $? -ne 0  ]; then
	echo "Cannot run inject_keeper_env.sh"
    exit 1
fi

function check_gpfs() {
    [[ $(ls /keeper) =~ "Stale file handle" ]] && err_and_exit "Stale file handle"
    [ ! -d "/keeper/${__GPFS_FILESET__}/" ] &&  err_and_exit "Cannot access /keeper/${__GPFS_FILESET__}"
    echo_green "/dev/gpfs_keeper is OK"
}


function restart_gpfs () {
    $0 status
    [ $? -eq 0 ] && err_and_exit "Keeper is running, please shutdown it first"
    mmshutdown && mmstartup
    sleep 10
    check_gpfs 
}

function check_en_dis_nginx () {
    RESULT=$(type "nginx_ensite" 2>/dev/null)
    if [ $? -ne 0 ] ; then
        err_and_exit "Please install nginx_[en|dis]site: https://github.com/perusio/nginx_ensite"
    fi
}

# switch HTTP configurations between default and maintenance
function switch_maintenance_mode () {
	local TO_DIS="${__MAINTENANCE_HTTP_CONF__}"
	local TO_EN="${__HTTP_CONF__}" 
	
	if [ -L "${__HTTP_CONF_ROOT_DIR__}/sites-enabled/$TO_EN" ]; then
		TO_DIS="${__HTTP_CONF__}"
		TO_EN="${__MAINTENANCE_HTTP_CONF__}"
	fi	

	nginx_dissite $TO_DIS
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot disable HTTP config $TO_DIS"
	fi
	
	nginx_ensite $TO_EN
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot enable HTTP config $TO_EN"
	fi

	service nginx reload
	if [ $? -ne 0  ]; then
		err_and_exit "Cannot reload HTTP $TO_EN"
	fi
}

function check_component_running() {
    name=$1
    cmd=$2
    if pid=$(pgrep -f "$cmd" 2>/dev/null); then
        echo "[$name] is running, pid: ${pid//$'\n'/, }"
    else
        echo_red "[$name] is not running"
        [[ $3 == "CRITICAL" ]] && RC=1
    fi
}

function check_seahub_running () {
    # if pid=$(pgrep -f "/seahub/manage.py" 2>/dev/null 1>&2 || pgrep -f "seahub.wsgi:application" 2>/dev/null 1>&2); then
    if pid=$(pgrep -f "/seahub/manage.py" 2>/dev/null || pgrep -f "seahub.wsgi:application" 2>/dev/null); then
        echo "[seahub] is running, pid: ${pid//$'\n'/, }"
    else
        echo_red "[seahub] is not runnig"
        [[ $1 == "CRITICAL" ]] && RC=1
    fi
}
#
# Write a polite log message with date and time
#
echo -e "\n \n About to perform $1 for seafile at `date -Iseconds` \n " >> ${seafile_init_log}
echo -e "\n \n About to perform $1 for seahub at `date -Iseconds` \n " >> ${seahub_init_log}

case "$1" in
        start|restart)
            systemctl ${1} memcached.service
            sudo -u ${user} ${script_path}/seafile.sh ${1} >> ${seafile_init_log}
            if [ $fastcgi = true ];
            then
                    sudo -u ${user} ${script_path}/seahub.sh ${1}-fastcgi ${fastcgi_port} >> ${seahub_init_log}
            else
                    sudo -u ${user} ${script_path}/seahub.sh ${1} >> ${seahub_init_log}
            fi
            ${seafile_dir}/scripts/catalog-service.sh ${1}
            service nginx ${1}
        ;;
        stop)
            sudo -u ${user} ${script_path}/seahub.sh ${1} >> ${seahub_init_log}
            sudo -u ${user} ${script_path}/seafile.sh ${1} >> ${seafile_init_log}
            ${seafile_dir}/scripts/catalog-service.sh ${1}
            systemctl ${1} memcached.service
        ;;
        restart-gpfs)
            restart_gpfs
        ;;
       switch-maintenance-mode)
            check_en_dis_nginx
            switch_maintenance_mode
        ;;
        status)
            RC=0
            check_component_running "seafile-controller" "seafile-controller -c ${default_ccnet_conf_dir}" "CRITICAL"
            check_seahub_running "CRITICAL"
            check_component_running "ccnet-server" "ccnet-server.*-c ${default_ccnet_conf_dir}" "CRITICAL"
            check_component_running "seaf-server" "seaf-server.*-c ${default_ccnet_conf_dir}" "CRITICAL"
            # TODO: check fileserver process: probably it is an old stuff, seaf-server makes the job
        #			check_component_running "fileserver" "fileserver.*-c ${default_ccnet_conf_dir}"
    #		check_component_running "seafdav" "wsgidav.server.run_server"
            check_component_running "seafevents" "seafevents.main" "CRITICAL"

            check_component_running "memcached" "memcached" "CRITICAL"
            check_component_running "elastic" "org.elasticsearch.bootstrap.Elasticsearch"  "CRITICAL"
            check_component_running "office/pdf preview" "soffice.bin.*StarOffice.ComponentContext"  "CRITICAL"
            check_component_running "keeper-catalog" "uwsgi.*catalog.ini"  "CRITICAL"
            [ $RC -eq 0 ] && echo_green "Status is OK" || echo_red "Status is not OK" 
            exit $RC
        ;;
        *)
            echo "Usage: /etc/init.d/seafile-server {start|stop|restart|status|restart-gpfs|switch-maintenance-mode}"
            exit 1
        ;;
esac

