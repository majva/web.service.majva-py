#!/bin/sh
set -e

cd /app

if [ -n "$POSTGRES_CONNECTION_STRING" ] || [ "$ENVIRONMENT" != "development" ]; then
    echo "[entrypoint] Running database migrations..."
    python src/infrastructure/scripts/run_migrations.py --upgrade
else
    echo "[entrypoint] Skipping migrations (POSTGRES_CONNECTION_STRING is not set)."
fi

echo "[entrypoint] Starting application..."
cd /app/src/host
exec python3 app.py
