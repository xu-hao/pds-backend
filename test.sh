#!/bin/bash
docker-compose --env-file test/env -f docker-compose.yml -f test/docker-compose.yml up --build -V --exit-code-from txrouter-test
