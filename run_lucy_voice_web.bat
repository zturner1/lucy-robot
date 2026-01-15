@echo off
REM Lucy Voice Web Interface Launcher

chcp 65001 > nul
cls

echo ============================================================
echo Lucy Voice Web Interface
echo ============================================================
echo.
echo Features:
echo   - Animated robot face
echo   - Voice input (hold mic button)
echo   - Voice output (automatic speech)
echo   - Text chat mode
echo   - Mobile-friendly (works on phones)
echo.
echo ============================================================
echo.

REM Get local IP for phone access
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do set IP=%%a
set IP=%IP:~1%

echo Starting server...
echo.
echo [PC] Open: http://localhost:8080
echo [Phone] Open: http://%IP%:8080
echo.
echo Press Ctrl+C to stop
echo.
echo ============================================================
echo.

set PYTHONIOENCODING=utf-8
python web/lucy_voice_web.py

pause
