#! /bin/bash

cd "$(dirname "$0")/.."
TIMESTAMP=$(date +%Y.%m.%d.%H%M%S)

# start mongodb
mongod --dbpath ../Project_Wiki_Data/db \
    --bind_ip 127.0.0.1 --port 27017 \
    --logpath ../Project_Wiki_Data/log/mongo_${TIMESTAMP}.log \
    --auth \
    --fork

echo "MongoDB Started"