@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "BACKEND_PORT=8100"
set "FRONTEND_PORT=5180"

if not exist "backend\.venv\Scripts\uvicorn.exe" (
  echo Python environment is missing.
  echo Running setup.bat first...
  echo.
  call "%~dp0setup.bat"
  if errorlevel 1 exit /b 1
)

if not exist "frontend\node_modules\" (
  echo frontend\node_modules is missing.
  echo Running setup.bat first...
  echo.
  call "%~dp0setup.bat"
  if errorlevel 1 exit /b 1
)

if not exist "backend\.env" (
  copy /Y backend\.env.example backend\.env >nul
)

echo Starting SANGAM backend on :%BACKEND_PORT% ...
start "SANGAM API" cmd /k "cd /d \"%~dp0backend\" && .venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port %BACKEND_PORT%"

timeout /t 3 >nul

echo Starting SANGAM frontend on :%FRONTEND_PORT% ...
start "SANGAM UI" cmd /k "cd /d \"%~dp0frontend\" && npm run dev -- --host 127.0.0.1 --port %FRONTEND_PORT%"

echo.
echo SANGAM App:   http://localhost:%FRONTEND_PORT%
echo SANGAM Login: http://localhost:%FRONTEND_PORT%/#/login
echo SANGAM API:   http://localhost:%BACKEND_PORT%/docs
echo Health:       http://localhost:%BACKEND_PORT%/api/health
echo.
exit /b 0
