@echo off

:: stop server
taskkill /IM pythonw.exe /f
echo Server stopped

:: stop MongoDB service
net stop MongoDB

sleep 1
