FROM python:3-alpine

RUN mkdir test
WORKDIR test

RUN pip3 install requests pytest pymongo docker pyyaml python-dateutil

COPY test/test_pds_backend.py test_pds_backend.py
COPY pds pds
COPY debug debug
COPY api api

ENTRYPOINT ["pytest"]



