#! /bin/bash

killall python PW_run.py
killall mongod
killall caddy -conf PW_Caddyfile
echo "Project Wiki Stopped"