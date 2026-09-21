@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "BACKEND_PORT=8100"

echo ========================================
echo  SANGAM local production deploy
echo ========================================
echo.

where node >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js was not found. Install Node.js 18+ and re-run.
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python was not found. Install Python 3.10+ and re-run.
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo Creating backend\.venv ...
  python -m venv backend\.venv
  if errorlevel 1 exit /b 1
)

echo Installing backend dependencies...
call backend\.venv\Scripts\pip.exe install -r backend\requirements.txt
if errorlevel 1 exit /b 1

if not exist "backend\.env" (
  copy /Y backend\.env.example backend\.env >nul
)

echo Installing frontend dependencies...
pushd frontend
call npm install
if errorlevel 1 (
  popd
  exit /b 1
)

REM Empty VITE_API_URL = same-origin API when served by FastAPI
set "VITE_API_URL="
call npm run build
if errorlevel 1 (
  popd
  echo ERROR: Frontend production build failed.
  exit /b 1
)
popd

echo Preparing website\ ^(static host package, gitignored^)...
if exist website rmdir /s /q website
mkdir website
xcopy /E /I /Y frontend\dist\* website\ >nul
if exist frontend\public\favicon.svg copy /Y frontend\public\favicon.svg website\favicon.svg >nul
echo /*    /index.html   200> website\_redirects
copy /Y website\index.html website\404.html >nul

echo Preparing backend\static\ ^(served by FastAPI^)...
if exist backend\static rmdir /s /q backend\static
mkdir backend\static
xcopy /E /I /Y frontend\dist\* backend\static\ >nul
if exist frontend\public\favicon.svg copy /Y frontend\public\favicon.svg backend\static\favicon.svg >nul

echo Ensuring database is initialized...
call backend\.venv\Scripts\python.exe backend\scripts\init_db.py
if errorlevel 1 exit /b 1

echo.
echo Built:
echo   website\        - optional static host package ^(gitignored^)
echo   backend\static\ - served by FastAPI
echo.
echo Starting SANGAM at http://localhost:%BACKEND_PORT%
echo Health: http://localhost:%BACKEND_PORT%/api/health
echo.
cd /d "%~dp0backend"
call .venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT%
