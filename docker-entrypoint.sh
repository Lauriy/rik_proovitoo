#!/bin/bash
set -e

python manage.py migrate --noinput &&
python manage.py collectstatic --noinput &&
uwsgi --ini /home/docker/rik_proovitöö/uwsgi.ini
