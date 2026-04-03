@echo off
REM Setup script for Windows - Backend and Frontend

echo ====================================
echo ITS Project Setup Script (Windows)
echo ====================================

REM Backend Setup
echo.
echo [1/4] Setting up Backend...
cd backend
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..
echo Backend setup complete!

REM Frontend Setup
echo.
echo [2/4] Setting up Frontend...
cd frontend
call npm install
echo. > .env.local
echo NEXT_PUBLIC_API_URL=http://localhost:8000 >> .env.local
cd ..
echo Frontend setup complete!

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo To start the project:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   .venv\Scripts\activate
echo   python main.py
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause
