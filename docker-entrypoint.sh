#!/bin/bash
set -e

python manage.py migrate --noinput

case "$DJANGO_ENV" in
  "development")
    python manage.py loaddata rik_proovitöö/fixtures/superuser.json
    python manage.py loaddata rik_proovitöö/fixtures/legal_entity.json
    python manage.py loaddata rik_proovitöö/fixtures/equity.json
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  "test")
    exec pytest
    ;;
  "production")
    python manage.py collectstatic --noinput
    exec uwsgi --ini /home/docker/rik_proovitöö/uwsgi.ini
    ;;
  *)
    echo "DJANGO_ENV must be set to 'development', 'test', or 'production'"
    exit 1
    ;;
esac