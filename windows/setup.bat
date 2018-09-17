@echo off

:: If MongoDB is installed with "Custom" installation option, 
:: the following directory should also be changed accordingly.
set mongod=C:\Program Files\MongoDB\Server\3.4\bin\mongod.exe
set mongo=C:\Program Files\MongoDB\Server\3.4\bin\mongo.exe

:: prompt for input
set /p username="Set MongoDB username: "
set /p password="Set MongoDB password: "

:: navigate to Project-Wiki folder
cd %~dp0\..
:: set wikidir to be current directory
set wikidir=%cd%
:: navigate to the parent directory of Project-Wiki
cd ..
:: set parentdir to be the parent directory of Project-Wiki
set parentdir=%cd%

:: If Project_Wiki_Data already exists, abort.
if exist %parentdir%\Project_Wiki_Data (
    echo Project_Wiki_Data already exists
    echo Please move it somewhere else and run this script again
    pause
    goto :eof 
) else (
    :: create Project_Wiki_Data folders
    mkdir Project_Wiki_Data\db Project_Wiki_Data\log Project_Wiki_Data\uploads Project_Wiki_Data\backup
    echo Project_Wiki_Data created
)

:: navigate to windows folder in Project-Wiki
cd %wikidir%\windows

(
echo systemLog:
echo     destination: file
echo     path: %parentdir%\Project_Wiki_Data\log\mongod.log
echo storage:
echo     dbPath: %parentdir%\Project_Wiki_Data\db
echo net:
echo     bindIp: 127.0.0.1
echo     port: 27017
echo security:
echo     authorization: enabled
) > "mongod.cfg"
echo mongod.cfg created
set mongodcfg=%wikidir%\windows\mongod.cfg

:: create MongoDB service
"%mongod%" --config "%mongodcfg%" --install

:: start MongoDB service
net start MongoDB

:: create admin account for mongo database
"%mongo%" admin --eval "db.createUser({user: '%username%', pwd: '%password%', roles:[{role:'root',db:'admin'}]});"

:: install python libraries
pip install -r requirements.txt

:: navigate back to Project-Wiki
cd ..
:: create an super admin account to manage Project Wiki
python manage.py create_admin

:: stop MongoDB service
net stop MongoDB

:: create a python script to start server
(
echo from manage import app
echo from waitress import serve
echo.
echo.
echo serve(app, listen='127.0.0.1:31415', threads=4^)
) > "PW_run.py"




