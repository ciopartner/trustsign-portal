#!/bin/bash
source /usr/local/bin/virtualenvwrapper.sh
source ~/.profile
source ~/.bashrc
export DJANGO_SETTINGS_MODULE='settings'
export LANG=pt_BR.UTF-8
workon trustsign-portal 

git pull
./portal/manage.py collectstatic --noinput

# Try to kill me!
kill $(cat /tmp/trustsign-portal.pid)

./portal/manage.py runfcgi socket=/tmp/trustsign-portal.sock pidfile=/tmp/trustsign-portal.pid maxrequests=2 --settings=settings

chmod g+w /tmp/trustsign-portal.sock
chgrp www-data /tmp/trustsign-portal.sock

