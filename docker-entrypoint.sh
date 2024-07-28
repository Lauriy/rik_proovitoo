#!/bin/bash
set -e

python manage.py migrate --noinput

if [ "$DJANGO_ENV" = "development" ]; then
    python manage.py loaddata rik_proovitöö/fixtures/superuser.json &&
    python manage.py loaddata rik_proovitöö/fixtures/legal_entity.json &&
    python manage.py loaddata rik_proovitöö/fixtures/equity.json
    python manage.py runserver 0.0.0.0:8000
fi

if [ "$DJANGO_ENV" = "test" ]; then
    pytest
fi

if [ "$DJANGO_ENV" = "production" ]; then
    python manage.py collectstatic --noinput
    uwsgi --ini /home/docker/rik_proovitöö/uwsgi.ini
fi

