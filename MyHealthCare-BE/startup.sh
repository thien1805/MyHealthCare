#!/bin/bash
set -e

echo "Starting Django application..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --no-input

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-4}" \
  --timeout 600 \
  --access-logfile - \
  --error-logfile - \
  myhealthcare.wsgi:application

