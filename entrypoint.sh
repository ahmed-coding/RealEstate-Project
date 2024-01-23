#!/usr/bin/env sh

echo 'Apply database migrations'

python manage.py migrate

echo 'Apply collectstatic'

python manage.py collectstatic --noinput

echo 'Apply spectacular schema'

python manage.py spectacular --color --file schema.yml

# Ensure that "python" is used to execute the provided command
exec "$@"
