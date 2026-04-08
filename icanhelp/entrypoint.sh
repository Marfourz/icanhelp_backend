#!/bin/bash

set -e 

python manage.py makemigrations
python manage.py migrate
python manage.py seed_db

if [ "$1" == 'gunicorn' ]; then

    exec gunicorn icanhelp.wsgi:application --bind 0.0.0.0:8000

else
    DJANGO_SETTINGS_MODULE=icanhelp.settings exec daphne -b 0.0.0.0 -p 8000 icanhelp.asgi:application


fi