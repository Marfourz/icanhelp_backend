#!/bin/bash

set -e 

python manage.py makemigrations
python manage.py migrate
python manage.py seed_db

if [ "$1" == 'gunicorn' ]; then

    exec gunicorn icanhelp.wsgi:application --bind 0.0.0.0:8000

else
    exec python manage.py runserver 0.0.0.0:8000


fi