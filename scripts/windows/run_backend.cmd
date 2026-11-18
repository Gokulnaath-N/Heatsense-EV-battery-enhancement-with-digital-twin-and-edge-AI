@echo off
setlocal
if not exist .venv\Scripts\python.exe (
  echo Virtual environment not found. Create it and install the project dependencies first.
  exit /b 1
)
.venv\Scripts\python.exe -m uvicorn heatsense.api.main:app --app-dir backend\src --reload --host 127.0.0.1 --port 8000
endlocal
