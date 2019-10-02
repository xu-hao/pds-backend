FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip3 install --no-cache-dir connexion pymongo docker-py

COPY api/openAPI3 /usr/src/app
COPY pds /usr/src/app/pds

EXPOSE 8080

ENTRYPOINT ["gunicorn"]

CMD ["-w", "4", "-b", "0.0.0.0:8080", "-k", "gevent", "server:create_app()"]