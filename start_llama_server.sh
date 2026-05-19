#!/bin/bash

# Kill any existing llama-server processes
echo "Stopping existing llama-server instances..."
pkill -f llama-server 2>/dev/null
sleep 2

# Get the local IP address (typically en0 on Mac)
IP_ADDR=$(ipconfig getifaddr en0 || hostname -I | awk '{print $1}')
PORT=1234

echo "-----------------------------------------------------------------"
echo "Starting llama-server as a drop-in replacement for LM Studio API"
echo "Other devices can connect at: http://${IP_ADDR}:${PORT}/v1"
echo "-----------------------------------------------------------------"

# Navigate to the llama.cpp server binary directory
cd /Users/ryan_chua/Desktop/llama.cpp/build/bin || exit

./llama-server \
  -m /Users/.lmstudio/models/lmstudio-community/gpt-oss-120b-GGUF/gpt-oss-120b-MXFP4-00001-of-00002.gguf \
  --host 0.0.0.0 \
  --port ${PORT} \
  --n-gpu-layers 999 \
  --ctx-size 65536 \
  --parallel 4 \
  --cont-batching \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --flash-attn on \
