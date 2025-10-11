#!/bin/bash

# Set environment variables for production
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:/app"

# Start the application with Gunicorn
exec gunicorn --config gunicorn_config.py app:app