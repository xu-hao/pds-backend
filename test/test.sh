#!/bin/bash

# source all the variables in the docker environment file
# to better simulate a more secure environment
# and also make variables available to test code in python scripts
export $(sed -e 's/=\(.*\)/="\1/g' -e 's/$/"/g' test/env.docker |grep -v "^#"| xargs)

MONGO_INITDB_ROOT_PASSWORD=example MONGO_NON_ROOT_PASSWORD=collection JWT_SECRET=secret ./docker-compose -f docker-compose.yml -f test/docker-compose.yml up --build -V --exit-code-from txrouter-test
