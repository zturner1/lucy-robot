@echo off
REM Lucy Robot - Windows Launcher
REM Sets UTF-8 encoding and starts Lucy web interface

chcp 65001 > nul
cls

echo ============================================================
echo Lucy Robot - Starting Web Interface
echo ============================================================
echo.

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags > nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama may not be running
    echo Start it with: ollama serve
    echo.
    pause
)

echo Opening Lucy web interface on http://localhost:8080
echo Press Ctrl+C to stop
echo.

python web/lucy_web.py

pause
