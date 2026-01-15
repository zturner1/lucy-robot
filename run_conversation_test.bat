@echo off
REM Run Lucy conversation tests with UTF-8 support

chcp 65001 > nul
cls

echo ============================================================
echo Lucy Conversation Test Suite
echo ============================================================
echo.

set PYTHONIOENCODING=utf-8

python test_conversations.py --auto

pause
