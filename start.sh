#!/bin/sh

# Install FastAPI dependencies
pip install fastapi[standard]

python event_collector/main.py & #Event collector
python data_ingestor/main.py & #Data ingestor

# Start backend in background
fastapi dev backend/api_server.py --port 8080 &

# Wait for backend to be up (check if port 8080 is open)
echo "Waiting for backend to start..."
while ! nc -z localhost 8080; do
  sleep 1
done

echo "Backend started, starting frontend..."
python frontend/main.py
