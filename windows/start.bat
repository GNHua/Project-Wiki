@echo off

:: start MongoDB service
net start MongoDB

:: navigate to Project-Wiki directory
cd %~dp0\..

:: start server in the background
start pythonw run.py
echo Server started
echo To shut down server, close this console, and run stop.bat as administator.

:: start caddy with configuration in PW_Caddyfile
caddy.exe -conf PW_Caddyfile
sleep 1
