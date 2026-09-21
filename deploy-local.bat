@echo off
REM Build portable website package + backend/static for FastAPI hosting
cd /d %~dp0frontend
call npm install
set VITE_API_URL=
call npm run build
cd /d %~dp0

if exist website rmdir /s /q website
mkdir website
xcopy /E /I /Y frontend\dist\* website\
if exist frontend\public\favicon.svg copy /Y frontend\public\favicon.svg website\favicon.svg >nul
echo /*    /index.html   200> website\_redirects
copy /Y website\index.html website\404.html >nul

if exist backend\static rmdir /s /q backend\static
mkdir backend\static
xcopy /E /I /Y frontend\dist\* backend\static\
if exist frontend\public\favicon.svg copy /Y frontend\public\favicon.svg backend\static\favicon.svg >nul

echo.
echo Built:
echo   website\          ^<- drop this folder on Netlify / static host
echo   backend\static\   ^<- served by FastAPI at http://localhost:8100
echo   index.html        ^<- redirects to website\
echo.
cd /d %~dp0backend
call .venv\Scripts\activate
echo Starting SANGAM at http://localhost:8100
uvicorn app.main:app --host 0.0.0.0 --port 8100
