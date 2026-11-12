@echo off
echo ===================================================
echo   Starting SAGE Evaluation Dashboard...
echo ===================================================

echo [1/2] Starting FastAPI Backend on http://localhost:8000...
start "SAGE Backend" cmd /k "%~dp0.venv\Scripts\python.exe -m uvicorn sage.dashboard_backend.main:app --port 8000"

echo [2/2] Checking Next.js production build...
if not exist "%~dp0sage\dashboard_frontend\.next" (
    echo Building Next.js frontend bundle...
    cd /d "%~dp0sage\dashboard_frontend" && npm.cmd run build
)

echo Starting Next.js Frontend Server on http://localhost:3000...
start "SAGE Frontend" cmd /k "cd /d %~dp0sage\dashboard_frontend && npm.cmd start"

echo Waiting 4 seconds for servers to initialize...
timeout /t 4 >nul

echo Opening browser at http://localhost:3000/leaderboard...
start http://localhost:3000/leaderboard

echo Done! Leave the two open terminal windows running during your session.
