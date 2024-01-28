FROM python:3.11.5-alpine
FROM postgresql
WORKDIR /usr/src/app/realEstate

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
apk add --no-cache build-base linux-headers musl-dev && \
apk add --no-cache gdal-dev geos-dev postgresql-dev cairo-dev libffi-dev && \
apk add --no-cache dos2unix && \
rm -rf /var/cache/apk/*

COPY ./requirements.txt /usr/src/app/realEstate/requirements.txt

RUN pip install --upgrade pip && \
pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/realEstate/entrypoint.sh

RUN dos2unix /usr/src/app/realEstate/entrypoint.sh
RUN chmod +x /usr/src/app/realEstate/entrypoint.sh
COPY . /usr/src/app/realEstate/

ENTRYPOINT [ "/usr/src/app/realEstate/entrypoint.sh" ]
