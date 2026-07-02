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
  python manage.py shell -c "
import os
from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.email = email
    user.save()
    print(f'Superuser \"{username}\" atualizado.')
except User.DoesNotExist:
    User.objects.create_superuser(username, email, password)
    print(f'Superuser \"{username}\" criado.')
" 2>&1 || true
fi

WORKERS=${GUNICORN_WORKERS:-$(nproc 2>/dev/null || echo 1)}
WORKERS=$((WORKERS * 2 + 1))

gunicorn core.wsgi:application \
    --bind 0.0.0.0:"${GUNICORN_PORT:-8000}" \
    --workers "$WORKERS" \
    --timeout 120 &
gunicorn_pid=$!
wait "$gunicorn_pid"
