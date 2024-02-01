[Documentation]
python manage.py spectacular --color --file schema.yml

[staticfile]
python manage.py collectstatic --noinput --clear

[Docker]
docker-compose up -d --build
<!-- get image list -->
docker image list
<!--  -->
docker exec -it containerName /bin/sh
<!-- windows problems fix -->
dos2unix core/entrypoint.sh 
docker build -t realestate-project-core core/
docker run -it --rm realestate-project-core /bin/ash
<!-- end windows problems fix -->
<!-- create superuser -->
docker exec -it containerName /bin/sh
python manage.py createsuperuser
exit

[UvicornServer]
uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload
