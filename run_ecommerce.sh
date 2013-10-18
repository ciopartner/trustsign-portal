#!/bin/bash
source /usr/local/bin/virtualenvwrapper.sh
source ~/.profile
source ~/.bashrc
export DJANGO_SETTINGS_MODULE='settings'
export LANG=pt_BR.UTF-8
export TRUSTSIGN_ENVIRONMENT='QAS'
workon trustsign-portal

git pull
ecommerce/manage.py collectstatic --noinput --settings=settings

# Try to kill me!
kill $(cat /tmp/trustsign-ecommerce.pid)

./ecommerce/manage.py runfcgi socket=/tmp/trustsign-ecommerce.sock pidfile=/tmp/trustsign-ecommerce.pid maxrequests=5 minspare=3 maxspare=3 maxchildren=8 --settings=settings

sudo chmod g+w /tmp/trustsign-ecommerce.sock
sudo chgrp www-data /tmp/trustsign-ecommerce.sock