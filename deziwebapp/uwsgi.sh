#!/bin/bash
source /home/kapilsharma/.bashrc
/home/kapilsharma/.virtualenvs/kapsite_venv/bin/uwsgi --ini /home/kapilsharma/www/deziwebapp/uwsgi.ini
#uwsgi -c /etc/uwsgi/apps-enabled/geonode.ini
