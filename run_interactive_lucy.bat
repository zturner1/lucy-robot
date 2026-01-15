@echo off
REM Run interactive Lucy conversation with UTF-8 support

chcp 65001 > nul
cls

echo ============================================================
echo Lucy - Interactive Conversation Mode
echo ============================================================
echo.
echo Commands:
echo   'exit' - End conversation
echo   'memory' - View what Lucy remembers
echo   'facts' - Show learned facts
echo   'idle' - See an idle thought
echo.
echo ============================================================
echo.

set PYTHONIOENCODING=utf-8

python test_conversations.py --interactive

pause
