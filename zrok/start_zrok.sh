#!/bin/bash

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_NAME="dutchb1api"
FRONTEND_NAME="dutchb1app"

echo "🚀 Starting zrok tunnels with custom names..."

# Start Backend Tunnel (Running in background)
echo "📡 Exposing Backend as $BACKEND_NAME on port $BACKEND_PORT..."

# 1. Try to reserve the name (ignore error if already reserved)
zrok reserve public http://localhost:$BACKEND_PORT --unique-name "$BACKEND_NAME" > /dev/null 2>&1

# 2. Start the shared reserved tunnel
zrok share reserved "$BACKEND_NAME" --headless > backend_zrok.log 2>&1 &
BACKEND_PID=$!

# Wait for URL to appear in logs (up to 30 seconds)
echo "⏳ Waiting for Backend URL..."
for i in {1..30}; do
    BACKEND_URL=$(grep -oE "https://[a-zA-Z0-9.-]+\.share\.zrok\.io" backend_zrok.log | head -n 1)
    if [ ! -z "$BACKEND_URL" ]; then
        break
    fi
    sleep 1
done

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Failed to capture Backend zrok URL after 30 seconds."
    cat backend_zrok.log
    kill $BACKEND_PID
    exit 1
fi

echo "✅ Backend URL: $BACKEND_URL"

# Update Frontend .env
echo "📝 Updating frontend .env with public backend URL..."
echo "VITE_API_BASE_URL=$BACKEND_URL/api" > frontend/.env

# Start Frontend Tunnel
echo "📡 Exposing Frontend as $FRONTEND_NAME on port $FRONTEND_PORT..."

# 1. Try to reserve the name (ignore error if already reserved)
zrok reserve public http://localhost:$FRONTEND_PORT --unique-name "$FRONTEND_NAME" > /dev/null 2>&1

# 2. Start the shared reserved tunnel
zrok share reserved "$FRONTEND_NAME"
