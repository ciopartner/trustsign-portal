#!/bin/bash
source /usr/local/bin/virtualenvwrapper.sh
source ~/.bashrc
export DJANGO_SETTINGS_MODULE='settings'
export TRUSTSIGN_ENVIRONMENT='QAS'
export LANG=pt_BR.UTF-8
workon trustsign-portal

git pull
./portal/manage.py collectstatic --noinput

# Try to kill me!
kill $(cat /tmp/trustsign-portal.pid)

./portal/manage.py runfcgi socket=/tmp/trustsign-portal.sock pidfile=/tmp/trustsign-portal.pid maxrequests=5 minspare=3 maxspare=3 maxchildren=8 --settings=settings

sudo chmod g+w /tmp/trustsign-portal.sock
sudo chgrp www-data /tmp/trustsign-portal.sock