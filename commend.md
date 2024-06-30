# [Documentation]
`python manage.py spectacular --color --file schema.yml`
# [staticfile]
`python manage.py collectstatic`

# [Docker]
### get image list
- `docker-compose up -d --build`
- `docker image list`
- ## other docker commends
    - `docker exec -it containerName /bin/sh`
    - ex.  `docker exec -it realestate-project-core /bin/sh`
    - `docker build -t realestate-project-core core/`
# windows problems fix 
`dos2unix core/entrypoint.sh `
`docker run -it --rm realestate-project-core /bin/ash`
# create superuser
## from docker
1. `docker exec -it containerName /bin/sh`
2. `python manage.py createsuperuser`
3. `exit`
## from terminal
1. `cd core`
2. `python manage.py makemigrations`
3. `python manage.py migrate`
4. `python manage.py createsuperuser`

# [Ubuntu Setup]
#### **Create venv for first time**
- `python -m venv venv`
#### **active venv**
- `source venv/bin/activate`
#### **install requierments**
 - `cd core`
 - `pip install -r requirements.txt`
#### **run project**
- `cd core`
 - `python manage.py runserver`

-------
# [UvicornServer]
`uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload`

# [Algolia Search]
## Algolia Setup for first time
` python.exe manage.py algolia_reindex`