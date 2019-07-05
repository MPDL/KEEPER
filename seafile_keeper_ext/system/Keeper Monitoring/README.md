
How to enable WOPI access events on Keeper Nodes

sudo ./keeper-oos-log-install.sh

What the script does:
1. Copies an updated configuration for memcached with higher verbosity level
2. Copies the keeper-oos-log.sh script into the keeper scripts folder 
3. Copies a file defining the keeper-oos-log systemd service
4. Copies configuration files that prevent rsyslog logging for memcached to preserve disk free space
5. Copies configuration files that increase the systemd journald logging rate limits to capture all memcached events
6  Reloads the systemd configuration
7. Restarts rsyslogd, systemd-journal, memcached
6. Enables the keeper-oos-log service
7. Starts the keeper-oos-log service
