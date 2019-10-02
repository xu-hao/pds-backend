#!/bin/bash
set -e

printenv

mongo <<EOF
use admin
db = db.getSiblingDB('$MONGO_INITDB_DATABASE')
db.createUser(
   {
     user: '$MONGO_NON_ROOT_USERNAME',
     pwd: '$MONGO_NON_ROOT_PASSWORD',
       roles: [ {
	   role: "readWrite",
	   db: '$MONGO_INITDB_DATABASE'
       } ]
   }
)
EOF

