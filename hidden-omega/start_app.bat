@echo off
echo Starting Liver Disease AI System...

start "Backend Server" cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --reload --port 8000"
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo Servers started! Access the app at http://localhost:3000
pause
