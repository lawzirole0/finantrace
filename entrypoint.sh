#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --log-file -
