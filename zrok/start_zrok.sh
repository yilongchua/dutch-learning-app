#!/bin/bash

set -u

# Configuration
BACKEND_PORT=8010
FRONTEND_PORT=5173
BACKEND_NAME="capybaraanddustybunnsapi"
FRONTEND_NAME="capybaraanddustybunnsapp"
LOOPBACK_HOST="127.0.0.1"

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

find_existing_reserved_share_target() {
    local share_name="$1"
    "$ZROK" overview 2>/dev/null | python3 - "$share_name" <<'PY'
import json, sys
name = sys.argv[1]
try:
    data = json.load(sys.stdin)
except Exception:
    print("")
    sys.exit(0)
for env in data.get("environments", []):
    for share in env.get("shares", []):
        if share.get("reserved") and share.get("shareToken") == name:
            print(share.get("backendProxyEndpoint", ""))
            sys.exit(0)
print("")
PY
}

ensure_reserved_share() {
    local share_name="$1"
    local target="$2"

    local existing_target
    existing_target="$(find_existing_reserved_share_target "$share_name")"
    if [ -n "$existing_target" ]; then
        if [ "$existing_target" = "$target" ]; then
            echo "✅ Reusing existing reserved share: $share_name -> $target"
            return 0
        fi
        echo "⚠️ Existing reserved share target mismatch for '$share_name':"
        echo "   current: $existing_target"
        echo "   wanted : $target"
        echo "   Recreating reserved share to avoid localhost/IPv6 tunnel issues..."
        "$ZROK" release "$share_name" >/dev/null 2>&1 || true
        sleep 1
    fi

    echo "🛠 Reserving new share: $share_name -> $target"
    local reserve_out
    if ! reserve_out="$("$ZROK" reserve public "$target" --unique-name "$share_name" 2>&1)"; then
        echo "❌ Failed to reserve '$share_name'."
        echo "$reserve_out"
        echo "Tip: the unique name may already be taken globally. Try a different BACKEND_NAME/FRONTEND_NAME."
        return 1
    fi

    local verify=""
    for _ in {1..8}; do
        verify="$(find_existing_reserved_share_target "$share_name")"
        if [ "$verify" = "$target" ]; then
            break
        fi
        sleep 1
    done

    if [ -z "$verify" ]; then
        if echo "$reserve_out" | grep -q "your reserved share token is '$share_name'"; then
            echo "⚠️ Reservation succeeded but was not yet visible in overview; continuing with '$share_name'."
        else
            echo "❌ Reserved share '$share_name' was not found after reservation."
            echo "$reserve_out"
            return 1
        fi
    fi

    echo "✅ Reserved share created: $share_name"
}

echo "✅ Using zrok binary: $ZROK"

# Clean up any existing reserved shares to start fresh
echo "🧹 Cleaning up existing zrok shares..."
"$ZROK" release "$BACKEND_NAME" >/dev/null 2>&1 || true
"$ZROK" release "$FRONTEND_NAME" >/dev/null 2>&1 || true
sleep 1

echo "🚀 Starting zrok tunnels with custom names..."

# Start Backend Tunnel (Running in background)
echo "📡 Exposing Backend as $BACKEND_NAME on port $BACKEND_PORT..."

# 1. Ensure reserved share exists
ensure_reserved_share "$BACKEND_NAME" "http://$LOOPBACK_HOST:$BACKEND_PORT" || exit 1

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
    echo "   Ensure backend is running on $LOOPBACK_HOST:$BACKEND_PORT on this machine."
fi

# Update Frontend .env with the keys actually used by frontend services
echo "📝 Updating frontend .env with public backend URL..."
cat > ../frontend/.env <<EOF
VITE_API_BASE_URL=$BACKEND_URL
VITE_DUTCH_API_URL=$BACKEND_URL/api/dutch
VITE_NEWS_API_URL=$BACKEND_URL/api/news
VITE_GRAPHICS_API_URL=$BACKEND_URL/api/graphics_generation/
VITE_SCHEDULER_API_URL=$BACKEND_URL/api/scheduler
VITE_MEDIA_LIBRARY_URL=$BACKEND_URL/api/media_library
VITE_MEDIA_BASE_URL=$BACKEND_URL
EOF
echo "✅ Wrote ../frontend/.env"
echo "   Restart frontend dev server after this change."

# Start Frontend Tunnel
echo "📡 Exposing Frontend as $FRONTEND_NAME on port $FRONTEND_PORT..."

# 1. Ensure reserved share exists
ensure_reserved_share "$FRONTEND_NAME" "http://$LOOPBACK_HOST:$FRONTEND_PORT" || exit 1

# 2. Start the shared reserved tunnel
"$ZROK" share reserved "$FRONTEND_NAME"
