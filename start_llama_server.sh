#!/bin/bash

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
  -m /Users/ryan_chua/.lmstudio/models/lmstudio-community/gpt-oss-120b-GGUF/gpt-oss-120b-MXFP4-00001-of-00002.gguf \
  --host 0.0.0.0 \
  --port ${PORT} \
  --n-gpu-layers 999 \
  --ctx-size 131072 \
  --parallel 4 \
  --cont-batching \
  --cache-type-k f16 \
  --cache-type-v f16 \
  --flash-attn on \
  --jinja \
  --chat-template "{%- if messages[0]['role'] == 'system' -%}{%- set system_message = messages[0]['content'] -%}{%- set loop_start = 1 -%}{%- else -%}{%- set system_message = 'You are a helpful assistant' -%}{%- set loop_start = 0 -%}{%- endif -%}<|start|>system<|message|>{{ system_message }}\nReasoning: medium<|end|>{%- for i in range(loop_start, messages|length) -%}{%- set message = messages[i] -%}<|start|>{{ message['role'] }}<|message|>{{ message['content'] }}<|end|>{%- endfor -%}<|start|>assistant<|channel|>final<|message|>" \
  --no-warmup
