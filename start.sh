#!/bin/sh

echo "Creating schema..."
python schema.py

echo "Seeding data..."
python seed.py

echo "Starting application..."
python app.py