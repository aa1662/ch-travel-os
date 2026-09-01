@echo off
chcp 65001 >nul
title CH Travel OS 2.0 伺服器與編輯器

echo ========================================================
echo   🚀 正在啟動 CH Travel OS 2.0 本機伺服器與編輯器...
echo ========================================================
echo.

cd /d "C:\Data\charlotte-ai-os-dev\ch-travel-os"

:: 檢查 port 8080 是否已經有 server 在跑
netstat -ano | findstr ":8080 " >nul
if %errorlevel% equ 0 (
    echo [INFO] 本機伺服器已在背景執行中 (Port 8080)。
) else (
    echo [INFO] 正在啟動 Python 本機伺服器...
    start "CH Travel OS Server" /min python tools/server.py
    timeout /t 2 >nul
)

echo.
echo [1/2] 正在開啟視覺化編輯器 (editor.html)...
start "" "http://127.0.0.1:8080/core/editor.html"

echo [2/2] 正在開啟旅程首頁 (docs/index.html)...
start "" "http://127.0.0.1:8080/docs/index.html"

echo.
echo ✅ 全部就緒！
echo --------------------------------------------------------
echo • 視覺化編輯器：http://127.0.0.1:8080/core/editor.html
echo • 本機旅程首頁：http://127.0.0.1:8080/docs/index.html
echo --------------------------------------------------------
timeout /t 3 >nul
