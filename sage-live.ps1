if (Test-Path "$PSScriptRoot\.venv\Scripts\python.exe") {
    & "$PSScriptRoot\.venv\Scripts\python.exe" -m sage_live.cli @args
} else {
    python -m sage_live.cli @args
}
