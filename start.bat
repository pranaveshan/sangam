@echo off
echo Starting SANGAM backend on :8100 ...
start "SANGAM API" cmd /k "cd /d %~dp0backend && .venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8100"
timeout /t 3 >nul
echo Starting SANGAM frontend on :5180 ...
start "SANGAM UI" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5180"
echo.
echo SANGAM App:  http://localhost:5180
echo SANGAM Login: http://localhost:5180/login
echo SANGAM API:  http://localhost:8100/docs
