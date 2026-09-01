@echo off
title CH Travel OS 2.0
cd /d "C:\Data\charlotte-ai-os-dev\ch-travel-os"

echo Starting CH Travel OS 2.0...

:: Check if port 8080 is already running
netstat -ano | findstr ":8080 " >nul
if %errorlevel% neq 0 (
    echo Starting Python local server on port 8080...
    start "CH Travel OS Server" /min python tools/server.py
    timeout /t 2 /nobreak >nul
)

echo Opening Editor and Home Page...
start "" "http://127.0.0.1:8080/core/editor.html"
start "" "http://127.0.0.1:8080/docs/index.html"

exit
