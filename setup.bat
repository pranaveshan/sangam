@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo  SANGAM setup (first-time install)
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python was not found on PATH.
  echo Install Python 3.10+ from https://www.python.org/downloads/
  echo Then re-run setup.bat
  exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js was not found on PATH.
  echo Install Node.js 18+ from https://nodejs.org/
  echo Then re-run setup.bat
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: npm was not found on PATH.
  echo Reinstall Node.js so that npm is included.
  exit /b 1
)

echo [1/5] Backend virtual environment...
if not exist "backend\.venv\Scripts\python.exe" (
  echo Creating backend\.venv ...
  python -m venv backend\.venv
  if errorlevel 1 (
    echo ERROR: Failed to create Python virtual environment.
    exit /b 1
  )
) else (
  echo backend\.venv already exists.
)

echo [2/5] Installing Python dependencies...
call backend\.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1
call backend\.venv\Scripts\pip.exe install -r backend\requirements.txt
if errorlevel 1 (
  echo ERROR: pip install failed.
  exit /b 1
)

echo [3/5] Backend environment file...
if not exist "backend\.env" (
  copy /Y backend\.env.example backend\.env >nul
  echo Created backend\.env from .env.example
) else (
  echo backend\.env already exists.
)

echo [4/5] Frontend dependencies...
if not exist "frontend\node_modules\" (
  echo Running npm install in frontend...
  pushd frontend
  call npm install
  if errorlevel 1 (
    popd
    echo ERROR: npm install failed.
    exit /b 1
  )
  popd
) else (
  echo frontend\node_modules already exists.
)

if not exist "frontend\.env" (
  if exist "frontend\.env.example" (
    copy /Y frontend\.env.example frontend\.env >nul
    echo Created frontend\.env from .env.example
  )
)

echo [5/5] Initializing database ^(SQLite + demo seed^)...
call backend\.venv\Scripts\python.exe backend\scripts\init_db.py
if errorlevel 1 (
  echo ERROR: Database initialization failed.
  exit /b 1
)

echo.
echo ========================================
echo  Setup complete.
echo  Next: run start.bat
echo ========================================
exit /b 0
