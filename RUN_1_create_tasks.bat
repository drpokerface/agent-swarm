@echo off
cd /d "%~dp0"
echo ============================================================
echo  agent-swarm  -  STEP 1: install deps + create the task board
echo ============================================================
findstr /R /C:"PASTE-YOUR" /C:"^GITHUB_TOKEN=b$" /C:"^GEMINI_API_KEY=a$" .env >nul 2>&1
if not errorlevel 1 (
    echo.
    echo   STOP: .env still has placeholder keys.
    echo   Your keys are still the dummies a / b. Double-click
    echo   SETUP_KEYS.bat, paste your two real keys, then run this again.
    echo.
    pause
    exit /b 1
)
python --version >nul 2>&1
if errorlevel 1 (
    echo   Python was not found on PATH. Install Python 3.10+ first.
    pause
    exit /b 1
)
echo Installing dependencies ...
python -m pip install -r requirements.txt
echo.
echo Asking the smart model to break the video goal into GitHub issues.
echo REVIEW the plan it prints, then type yes to approve it.
echo.
python owner.py "Create an original ~2 minute animated comedy short as a single MP4 file, final.mp4 (1280x720, with audio: character voices and music/SFX). Build it around one original funny joke or comedic premise in the irreverent, satirical adult-animation style aimed at the same audience as Family Guy or South Park: punchy dialogue, fast pacing, cutaway gags. You have full creative control over the joke, characters, art style and animation technique - simple South-Park-style cutout animation is fine. Hard requirements: a real watchable video close to 120 seconds, synced dialogue audio, a hook in the first 5 seconds, no dead air, and a punchline payoff at the end."
echo.
echo If you approved the plan: now double-click RUN_2_worker.bat
pause
