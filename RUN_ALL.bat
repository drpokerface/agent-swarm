@echo off
setlocal
cd /d "%~dp0"
rem -- v6 one-click launcher: kills old swarm windows, revert-proofs the code,
rem -- (re)plans if you say yes, starts the arbiter window and the worker.
taskkill /f /fi "WINDOWTITLE eq swarm-arbiter*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq swarm-worker*" >nul 2>&1
title swarm-worker
echo ================================================================
echo   agent-swarm v6 : setup, code sync, plan, arbiter, worker
echo ================================================================
findstr /C:"PASTE-YOUR" .env >nul 2>&1
if errorlevel 1 goto keysok
echo.
echo Your two API keys are not set yet. Paste them now - right-click pastes.
set "GT="
set /p GT=GitHub token, starts with github_pat_ :
if "%GT%"=="" echo Nothing pasted - run again. & exit /b 1
set "GK="
set /p GK=Gemini API key, starts with AIza :
if "%GK%"=="" echo Nothing pasted - run again. & exit /b 1
powershell -NoProfile -Command "(Get-Content .env) -replace 'GITHUB_TOKEN=.*','GITHUB_TOKEN=%GT%' -replace 'GEMINI_API_KEY=.*','GEMINI_API_KEY=%GK%' | Set-Content -Encoding ascii .env"
echo Keys saved to .env - they stay on this computer only.
:keysok
python --version >nul 2>&1 || (echo Python not found on PATH - install Python 3.10+ first. & pause & exit /b 1)
echo Installing dependencies ...
python -m pip install -q -r requirements.txt
echo.
echo Revert-proofing: committing the swarm code into the repo so a publish
echo failure can never reset it to an older version again ...
git add seed.py worker.py owner.py status.py RUN_ALL.bat RUN_1_create_tasks.bat RUN_2_worker.bat CHECK_STATUS.bat SETUP_KEYS.bat requirements.txt README.md .env.example .gitignore >nul 2>&1
git commit -m "swarm code v6" >nul 2>&1
git pull --rebase >nul 2>&1
git push >nul 2>&1
set "GOAL=Create an original ~2 minute animated comedy short as a single MP4 file, final.mp4 (1280x720, with audio: character voices and music/SFX). Build it around one original funny joke or comedic premise in the irreverent, satirical adult-animation style aimed at the same audience as Family Guy or South Park: punchy dialogue, fast pacing, cutaway gags. You have full creative control over the joke, characters, art style and animation technique - simple South-Park-style cutout animation is fine. Hard requirements: a real watchable video close to 120 seconds, synced dialogue audio, a hook in the first 5 seconds, no dead air, and a punchline payoff at the end."
echo.
echo The planner will now propose a task board. Type yes to create it, or no
echo to skip planning and just resume the existing board.
echo.
python owner.py "%GOAL%"
echo.
echo Starting the arbiter in its own window (reviews proposals and questions) ...
start "swarm-arbiter" cmd /k python owner.py --watch "%GOAL%"
echo Starting the worker. Leave this terminal running - Ctrl-C stops it.
echo Progress: run CHECK_STATUS.bat, or watch the repo issues on GitHub.
echo.
python worker.py
pause
