#!/bin/bash
set -e

echo "Starting Django application..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --no-input

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 --access-logfile=- --error-logfile=- myhealthcare.wsgi:application

