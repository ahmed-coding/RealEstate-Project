[Documentation]
python manage.py spectacular --color --file schema.yml

[staticfile]
python manage.py collectstatic

[Docker]
docker-compose up -d --build
docker exec -it containerName /bin/sh
docker exec -it ds-coreAPIs /bin/sh

[UvicornServer]
uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload
