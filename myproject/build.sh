#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py migrate --noinput

if [ "$CREATE_SUPERUSER" = "True" ]; then
  python manage.py createsuperuser \
    --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL"
fi

python manage.py collectstatic --noinput
