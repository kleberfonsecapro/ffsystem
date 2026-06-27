#!/bin/bash
set -e
set -o pipefail

cleanup() {
    echo "Recebido sinal de parada. Encerrando servidor..."
    kill -TERM "$gunicorn_pid" 2>/dev/null || true
    wait "$gunicorn_pid" 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>&1 || true
fi

WORKERS=${GUNICORN_WORKERS:-$(nproc 2>/dev/null || echo 1)}
WORKERS=$((WORKERS * 2 + 1))

gunicorn core.wsgi:application \
    --bind 0.0.0.0:"${GUNICORN_PORT:-8000}" \
    --workers "$WORKERS" \
    --timeout 120 &
gunicorn_pid=$!
wait "$gunicorn_pid"
