@echo off
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -m sage_live.cli %*
) else (
    python -m sage_live.cli %*
)
