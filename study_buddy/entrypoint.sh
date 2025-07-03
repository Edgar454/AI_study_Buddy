#!/bin/bash
set -e

# Start Supervisor (manages FastAPI and Celery)
echo "Starting Supervisor..."
supervisord -c /etc/supervisord.conf &

# Wait for FastAPI to be ready at root "/"
echo "Waiting for FastAPI to be ready..."
until curl -s http://localhost:8000/ > /dev/null; do
  echo "FastAPI not ready yet..."
  sleep 2
done

echo "FastAPI is ready. Running setup_roles.py..."
python /app/src/setup_services.py

# Keep container alive by waiting on Supervisor
wait
