#!/bin/bash

# Azure deployment script
# This script will be run by Azure during deployment

echo "Starting deployment..."

# Navigate to backend directory
cd backend

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate --no-input

echo "Deployment completed successfully!"

