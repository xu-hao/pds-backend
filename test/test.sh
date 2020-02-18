#!/bin/bash

# source all the variables in the docker environment file
# to better simulate a more secure environment
# and also make variables available to test code in python scripts

# get tag from this commit.
# if there's no tag, use 'unstable' to tag the container on commits to master
TX_TAG=`git describe --exact-match --tags $(git log -n1 --pretty='%h')  2> /dev/null; `
if [ "${TX_TAG}" == "" ] ; then TX_TAG='unstable'; fi
echo "TX_TAG=${TX_TAG}" > env.TAG

set -o allexport
source env.TAG
source test/env.docker
set +o allexport

# note that the environmenal variables set above
# will override any .env variables
# setting them explicitly here avoids any ambiguity

# add other MONGO creds here?
MONGO_INITDB_ROOT_PASSWORD=example MONGO_NON_ROOT_PASSWORD=collection JWT_SECRET=secret docker-compose -f docker-compose.yml -f test/docker-compose.yml up --build -V --exit-code-from txrouter-test

### save info on how docker containers were configured
MONGO_INITDB_ROOT_PASSWORD=example MONGO_NON_ROOT_PASSWORD=collection JWT_SECRET=secret docker-compose -f docker-compose.yml -f test/docker-compose.yml config > test/config.out


env > test/env.out
