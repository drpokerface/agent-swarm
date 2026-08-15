@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo  agent-swarm - key setup  (keys stay on THIS computer only)
echo ============================================================
echo.
echo Tip: paste into this window with a RIGHT-CLICK.
echo.
set "GT="
set /p GT=Paste your GitHub token (from the browser tab) and press Enter: 
if "%GT%"=="" echo Nothing pasted - run this again. & pause & exit /b 1
set "GK="
set /p GK=Paste your Gemini API key (other browser tab) and press Enter: 
if "%GK%"=="" echo Nothing pasted - run this again. & pause & exit /b 1
powershell -NoProfile -Command "(Get-Content .env) -replace '^GITHUB_TOKEN=.*','GITHUB_TOKEN=%GT%' -replace '^GEMINI_API_KEY=.*','GEMINI_API_KEY=%GK%' | Set-Content -Encoding ascii .env"
findstr /C:"PASTE-YOUR" .env >nul 2>&1
if not errorlevel 1 (
    echo Something went wrong - placeholders are still in .env. Run this again.
    pause
    exit /b 1
)
echo.
echo Keys saved. Next: double-click RUN_1_create_tasks.bat
pause
