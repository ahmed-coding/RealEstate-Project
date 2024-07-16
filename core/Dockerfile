FROM python:3.11.5-alpine

WORKDIR /usr/src/app/realEstate

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add --no-cache build-base linux-headers musl-dev && \
    apk add --no-cache  postgresql-dev cairo-dev libffi-dev && \
    apk add --no-cache dos2unix && \
    rm -rf /var/cache/apk/*

COPY ./requirements.txt /usr/src/app/realEstate/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /usr/src/app/realEstate/

CMD ["sh", "-c", " \
    echo 'Apply database migrations' && \
    python manage.py makemigrations && \
    echo 'Apply database migrate' && \
    python manage.py migrate && \
    echo 'Apply collectstatic' && \
    python manage.py collectstatic --noinput && \
    echo 'Apply Crontab Jobs' && \
    python manage.py crontab add && \
    echo 'Apply spectacular schema' && \
    python manage.py spectacular --color --file schema.yml && \
    python manage.py runserver 0.0.0.0:8000"]

RUN python manage.py crontab add && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    python manage.py spectacular --color --file schema.yml
