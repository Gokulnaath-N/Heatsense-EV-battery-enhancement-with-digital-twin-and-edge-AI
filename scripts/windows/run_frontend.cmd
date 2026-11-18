@echo off
setlocal
cd frontend
if not exist node_modules (
  echo Frontend dependencies are not installed. Run npm install first.
  exit /b 1
)
npm run dev
endlocal
