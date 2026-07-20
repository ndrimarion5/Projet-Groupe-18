#!/bin/sh
set -eu

uvicorn app.api:app --host 127.0.0.1 --port 8000 &
API_PID="$!"

cleanup() {
    kill "$API_PID" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

python - <<'PY'
import socket
import sys
import time

deadline = time.time() + 180
while time.time() < deadline:
    try:
        with socket.create_connection(("127.0.0.1", 8000), timeout=2):
            sys.exit(0)
    except OSError:
        time.sleep(1)

print("L'API FastAPI n'a pas demarre sur le port 8000.", file=sys.stderr)
sys.exit(1)
PY

exec streamlit run app/main.py \
    --server.address 0.0.0.0 \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false