#!/bin/bash
# 1. Start the POT provider
chmod +x pot_server.sh
./pot_server.sh

# 2. Start your FastAPI app
uvicorn main:app --host 0.0.0.0 --port $PORT