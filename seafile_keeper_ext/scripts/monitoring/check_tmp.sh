#!/bin/bash


WC="usr/bin/wc"
DIFF="/usr/bin/diff"
RM="/bin/rm"
ECHO="/bin/echo"
CAT="/bin/cat"
LS="/bin/ls"
CRITICAL=600
WARNING=400

FILES=`/bin/ls -l /tmp/| /usr/bin/wc -l`

if [ $FILES -gt $CRITICAL ]
then
        $ECHO Critical: $FILES
        exitstatus=2
elif [ $FILES -gt $WARNING ]
then
        $ECHO Warning: $FILES
        exitstatus=1
else    $ECHO OK: $FILES
        exitstatus=0
fi

exit $exitstatus
