#!/bin/bash

set -u

# Configuration
BACKEND_PORT=8010
FRONTEND_PORT=5173
BACKEND_NAME="dutchb1apiv2"
FRONTEND_NAME="dutchb1appv2"

# Resolve zrok binary
resolve_zrok_bin() {
    if [ -n "${ZROK_BIN:-}" ] && [ -x "${ZROK_BIN}" ]; then
        echo "${ZROK_BIN}"
        return 0
    fi
    if command -v zrok >/dev/null 2>&1; then
        command -v zrok
        return 0
    fi
    for candidate in "$HOME/.zrok/bin/zrok" "$HOME/.local/bin/zrok" "/usr/local/bin/zrok" "/opt/homebrew/bin/zrok"; do
        if [ -x "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

ZROK="$(resolve_zrok_bin)" || {
    echo "❌ zrok binary not found."
    echo "Install zrok or set ZROK_BIN to the full binary path."
    echo "Example: export ZROK_BIN=\$HOME/.zrok/bin/zrok"
    exit 1
}

echo "✅ Using zrok binary: $ZROK"
echo "🚀 Starting zrok tunnels with custom names..."

# Start Backend Tunnel (Running in background)
echo "📡 Exposing Backend as $BACKEND_NAME on port $BACKEND_PORT..."

# 1. Try to reserve the name (ignore error if already reserved)
"$ZROK" reserve public http://localhost:$BACKEND_PORT --unique-name "$BACKEND_NAME" > /dev/null 2>&1

# 2. Start the shared reserved tunnel
"$ZROK" share reserved "$BACKEND_NAME" --headless > backend_zrok.log 2>&1 &
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
    if kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
        kill "$BACKEND_PID"
    fi
    exit 1
fi

echo "✅ Backend URL: $BACKEND_URL"

# Quick backend preflight check through public URL
echo "🔎 Verifying backend health via tunnel..."
if ! curl -sSf "$BACKEND_URL/api/dutch/health" >/dev/null 2>&1; then
    echo "⚠️ Backend tunnel is up but /api/dutch/health did not respond successfully."
    echo "   Ensure backend is running on localhost:$BACKEND_PORT on this machine."
fi

# Update Frontend .env with the keys actually used by frontend services
echo "📝 Updating frontend .env with public backend URL..."
cat > ../frontend/.env <<EOF
VITE_DUTCH_API_URL=$BACKEND_URL/api/dutch
VITE_NEWS_API_URL=$BACKEND_URL/api/news
VITE_GRAPHICS_API_URL=$BACKEND_URL/api/graphics_generation/
VITE_SCHEDULER_API_URL=$BACKEND_URL/api/scheduler
VITE_MEDIA_BASE_URL=$BACKEND_URL
EOF
echo "✅ Wrote ../frontend/.env"
echo "   Restart frontend dev server after this change."

# Start Frontend Tunnel
echo "📡 Exposing Frontend as $FRONTEND_NAME on port $FRONTEND_PORT..."

# 1. Try to reserve the name (ignore error if already reserved)
"$ZROK" reserve public http://localhost:$FRONTEND_PORT --unique-name "$FRONTEND_NAME" > /dev/null 2>&1

# 2. Start the shared reserved tunnel
"$ZROK" share reserved "$FRONTEND_NAME"
