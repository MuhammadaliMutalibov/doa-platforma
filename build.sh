#!/usr/bin/env bash
# Render build skripti — xatolik bo'lsa to'xtaydi
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
