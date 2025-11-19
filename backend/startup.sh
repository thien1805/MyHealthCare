#!/bin/bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install --upgrade pip
pip install --upgrade setuptools
pip install --upgrade wheel
pip install --upgrade gunicorn
pip install --upgrade dj-database-url
pip install --upgrade whitenoise
pip install --upgrade psycopg2-binary
pip install --upgrade django-extensions
pip install --upgrade djangorestframework
pip install --upgrade djangorestframework-simplejwt
pip install --upgrade django-cors-headers
pip install --upgrade django-filter
pip install --upgrade django-rest-framework-simplejwt
pip install --upgrade django-rest-framework-simplejwt-blacklist

python manage.py migrate --no-input
python manage.py collectstatic --no-input
gunicorn --bind=0.0.0.0 --timeout 600 myhealthcare.wsgi:application


