#! /bin/bash

kill -9 `ps -ef | grep mongod | grep -v grep | awk '{print $2}'`
echo "MongoDB Stopped"