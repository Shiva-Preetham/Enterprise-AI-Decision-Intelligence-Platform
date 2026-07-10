#!/usr/bin/env bash

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A workers.celery_app worker --loglevel=info &

# Start FastAPI application in the foreground
echo "Starting FastAPI server..."
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
