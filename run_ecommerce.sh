#!/bin/bash
source /usr/local/bin/virtualenvwrapper.sh
source ~/.profile
source ~/.bashrc
export DJANGO_SETTINGS_MODULE='ecommerce.settings'
export LANG=pt_BR.UTF-8
workon trustsign-portal 

git pull
ecommerce/manage.py collectstatic --noinput

# Try to kill me!
kill $(cat /tmp/trustsign-ecommerce.pid)

./ecommerce/manage.py runfcgi socket=/tmp/trustsign-ecommerce.sock pidfile=/tmp/trustsign-ecommerce.pid maxrequests=4

chmod g+w /tmp/trustsign-ecommerce.sock
chgrp www-data /tmp/trustsign-ecommerce.sock

