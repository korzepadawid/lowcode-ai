#!/bin/sh

python manage.py collectstatic --noinput && \
python manage.py makemigrations && \
python manage.py migrate && \
gunicorn --bind 0.0.0.0:8000 lowcode_ai.wsgi:application
