@echo off
cd /d "%~dp0"
echo ============================================================
echo  agent-swarm  -  STEP 2: the worker  (leave this window open)
echo ============================================================
echo It claims issues, runs seed.py on each, publishes artifacts,
echo verifies them, and closes them - fully automatic from here.
echo Stop anytime: Ctrl-C or close this window.
echo Watch progress: CHECK_STATUS.bat, or the issues page of
echo github.com/drpokerface/agent-swarm
echo.
python worker.py
pause
