# Short-Description: Starts Seafile Server
# Description:       starts Seafile Server
### END INIT INFO

# Change the value of "user" to linux user name who runs seafile
user=root

# Change the value of "seafile_dir" to your path of seafile installation
# usually the home directory of $user
seafile_dir=/opt/seafile
script_path=${seafile_dir}/seafile-server-latest
seafile_init_log=${seafile_dir}/logs/seafile.init.log
seahub_init_log=${seafile_dir}/logs/seahub.init.log

# Change the value of fastcgi to true if fastcgi is to be used
fastcgi=true
# Set the port of fastcgi, default is 8000. Change it if you need different.
fastcgi_port=8001

#
# Write a polite log message with date and time
#
echo -e "\n \n About to perform $1 for seafile at `date -Iseconds` \n " >> ${seafile_init_log}
echo -e "\n \n About to perform $1 for seahub at `date -Iseconds` \n " >> ${seahub_init_log}

case "$1" in
        start)
                sudo -u ${user} ${script_path}/seafile.sh ${1} >> ${seafile_init_log}
                if [ $fastcgi = true ];
                then
                        sudo -u ${user} ${script_path}/seahub.sh ${1}-fastcgi ${fastcgi_port} >> ${seahub_init_log}
                else
                        sudo -u ${user} ${script_path}/seahub.sh ${1} >> ${seahub_init_log}
                fi
        ;;
        restart)
                sudo -u ${user} ${script_path}/seafile.sh ${1} >> ${seafile_init_log}
                if [ $fastcgi = true ];
                then
                        sudo -u ${user} ${script_path}/seahub.sh ${1}-fastcgi ${fastcgi_port} >> ${seahub_init_log}
                else
                        sudo -u ${user} ${script_path}/seahub.sh ${1} >> ${seahub_init_log}
                fi
        ;;
        stop)
                sudo -u ${user} ${script_path}/seahub.sh ${1} >> ${seahub_init_log}
                sudo -u ${user} ${script_path}/seafile.sh ${1} >> ${seafile_init_log}
        ;;
        *)
                echo "Usage: /etc/init.d/seafile-server {start|stop|restart}"
                exit 1
        ;;
esac

