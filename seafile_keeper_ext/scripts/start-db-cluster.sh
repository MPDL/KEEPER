#!/bin/bash
#Has to be started only once if not any of nodes is running
systemctl set-environment _WSREP_NEW_CLUSTER='--wsrep-new-cluster' && systemctl start mysql && systemctl set-environment _WSREP_NEW_CLUSTER=''
