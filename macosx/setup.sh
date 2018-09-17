#! /bin/bash

cd "$(dirname "$0")/.."

echo "Type database username followed by [ENTER]:"
# prompt for input
read username

echo "Type database password followed by [ENTER]:"
# prompt for input
read password

# create data directories
if [ ! -d "../Project_Wiki_Data" ]; then
  mkdir -p ../Project_Wiki_Data/db ../Project_Wiki_Data/log ../Project_Wiki_Data/uploads ../Project_Wiki_Data/backup
else
  echo "Project_Wiki_Data already exists"
  echo "Move it elsewhere, and run this scripts again"
  exit 1
fi

# mongod launched in background
mongod --dbpath ../Project_Wiki_Data/db \
    --bind_ip 127.0.0.1 --port 27017 \
    --logpath ../Project_Wiki_Data/log/mongo_setup.log \
    --auth \
    --fork

# wait for mongod to start
sleep 3

# create admin account for database
mongo admin --eval "db.createUser({user: '$username', pwd: '$password', roles:[{role:'root',db:'admin'}]});"

# install python libraries
pip install -r macosx/requirements.txt

# create an super admin account to manage Project Wiki
python manage.py create_admin

# create a python script to start server
rm -f PW_run.py
cat <<EOF >> PW_run.py
from manage import app
from waitress import serve


serve(app, listen='127.0.0.1:31415', threads=4)
EOF

# kill mongod process
kill -9 `ps -ef | grep mongod | grep -v grep | awk '{print $2}'`
