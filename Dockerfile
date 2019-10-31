FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk add gcc musl-dev
RUN apk add libffi-dev
RUN apk add openssl-dev

RUN apk add openssl
RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=US/ST=North Carolina/L=Chapel Hill/O=UNC Chapel Hill/OU=RENCI/CN=pdsb"

RUN pip3 install --no-cache-dir connexion pymongo docker gunicorn[gevent] flask-cors python-dateutil python-jose[cryptography]

COPY api /usr/src/app/api
COPY pds /usr/src/app/pds
COPY sc.py /usr/src/app/sc.py

EXPOSE 8080

ENTRYPOINT ["gunicorn"]

CMD ["-w", "4", "-b", "0.0.0.0:8080", "--certfile", "cert.pem", "--keyfile", "key.pem", "-k", "gevent", "-c", "sc.py", "api.server:create_app()"]