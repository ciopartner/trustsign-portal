#!/bin/bash
lockfile=/tmp/lock-django-cron.file

if [ ! -e $lockfile ]; then
   touch $lockfile
   export WORKON_HOME=$HOME/envs
   export PROJECT_HOME=$HOME/workspace
   source /usr/local/bin/virtualenvwrapper.sh
   workon trustsign-portal
   ecommerce/manage.py runcrons >> ~/workspace/trustsign-portal/logs/logfile-cron.log 2>&1
   rm $lockfile
else
   echo "script already running"
fi
