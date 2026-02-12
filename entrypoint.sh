#!/bin/bash
set -e

echo "Waiting for database..."
sleep 5

echo "Running migrations..."
python manage.py migrate

echo "Loading fuel stations..."
python manage.py load_fuel_station_and_prices \
    --file /data/fuel-prices-for-be-assessment.csv

echo "Geocoding missing stations..."
python manage.py geocode_missing \
    --file /data/fuel-prices-for-be-assessment.csv

echo "Starting Django..."
python manage.py runserver 0.0.0.0:8000
