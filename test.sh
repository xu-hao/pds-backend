#!/bin/bash
MONGO_INITDB_ROOT_PASSWORD=example MONGO_NON_ROOT_PASSWORD=collection JWT_SECRET=secret docker-compose --env-file test/env -f docker-compose.yml -f test/docker-compose.yml up --build -V --exit-code-from txrouter-test
