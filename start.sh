#!/bin/sh

pip install fastapi[standard]

python event_collector/main.py & # Event collector
python data_ingestor/main.py & # Data ingestor

fastapi dev backend/api_server.py --port 8080 &

echo "Waiting for backend to start..."
while ! nc -z localhost 8080; do
  sleep 1
done

echo "Backend started, starting frontend..."
python frontend/main.py
