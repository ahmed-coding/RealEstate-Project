#!/bin/ash

echo "Apply database migrations"

pip install requirements.txt

python manage.py makemigrations

echo "Apply database migrate"

python manage.py migrate

echo "Apply collectstatic"

python manage.py collectstatic --noinput

echo "Apply spectacular schema"

python manage.py spectacular --color --file schema.yml

exec "$@"
