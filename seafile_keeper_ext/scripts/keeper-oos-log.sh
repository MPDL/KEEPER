#!/bin/bash
#
#   What this script does:
#   Tails the memcached logs, looks for memcache WOPI keys 'set' action.
#   When a 'set' action is found, it queries the memcached for details then it outputs to syslog (local1.info, label: keeper-oos) the following information
#   about the wopi access token: timestamp, library, user, file, extension.

MS='__MEMCACHED_SERVER__'
memcached_host=${MS%:*}

journalctl -u memcached -f | grep --line-buffered wopi_access_token | grep --line-buffered set | awk '{print $1" "$2" "$3" "$8}; system("")' | while read line
do
  wopi_token_full=$line;
  wopi_token=`echo $wopi_token_full | awk '{print $4}'`
  datetime=`echo $wopi_token_full | awk '{print $1" "$2" "$3}'`
  isotime=`date --date="$datetime" -Iseconds`

  wopi_access_token=`echo $wopi_memcache | awk -F'_' '{print $4}' | awk '{print $1}'`
  library=`echo $wopi_token | xargs -L1 -I{} bash -c 'echo -en "get {}\nquit\n" | nc '$memcached_host' 11211' | tr '\n' ' ' | awk -F "\x0000" '{print $4}'| awk -F '\x71' '{print $1}'`
  filename=`echo $wopi_token | xargs -L1 -I{} bash -c 'echo -en "get {}\nquit\n" | nc '$memcached_host' 11211' | tr '\n' ' ' | awk -F "\x0000" '{print $11}'| awk -F '\x71' '{print $1}'`
  extension=${filename##*.}
  username=`echo $wopi_token | xargs -L1 -I{} bash -c 'echo -en "get {}\nquit\n" | nc '$memcached_host' 11211' | tr '\n' ' ' | awk -F "\x0000" '{print $8}' | awk -F '\x71' '{print $1}'`

  output=$isotime" "$library" "$username" \""$filename"\" ."$extension
  echo $output | logger -t 'keeper-oos' -p local1.info
done
