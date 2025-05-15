#!/bin/bash

# Start MongoDB in the background (if not already running)
echo "Starting MongoDB..."
if pgrep -x mongod > /dev/null; then
  echo "MongoDB já está rodando."
else
  mkdir -p /data/db
  mongod --dbpath /data/db --bind_ip_all > mongodb.log 2>&1 &
  sleep 3
  echo "MongoDB iniciado."
fi

# Start FastAPI app
cd src

echo "Starting FastAPI (Uvicorn)..."
uvicorn app:app --reload --host 0.0.0.0 --port 8000
