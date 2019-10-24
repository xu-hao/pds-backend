FROM python:3-alpine

RUN mkdir test
WORKDIR test

RUN pip3 install requests pytest pymongo docker pyyaml

COPY test/test_pds_backend.py test_pds_backend.py
COPY pds pds
COPY debug debug
COPY api/openAPI3 api

ENTRYPOINT ["pytest"]



