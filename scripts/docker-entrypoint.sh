#!/bin/sh
set -e
mkdir -p "${STORAGE_ROOT:-/data/storage}"
if [ -n "${INSIGHTFACE_ROOT}" ]; then
  mkdir -p "${INSIGHTFACE_ROOT}"
fi
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
