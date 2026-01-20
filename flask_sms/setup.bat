@echo off
echo ================================
echo Flask SMS - Setup Script
echo ================================
echo.

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created

echo.
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

echo.
echo [3/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [4/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo ✓ .env file created from template
    echo ⚠ Please edit .env file with your configuration
) else (
    echo ! .env file already exists, skipping...
)

echo.
echo [5/5] Creating database and seeding data...
python run.py
timeout /t 3 /nobreak > nul
python seed.py
if errorlevel 1 (
    echo ERROR: Failed to seed database
    pause
    exit /b 1
)

echo.
echo ================================
echo ✅ Setup Complete!
echo ================================
echo.
echo To run the application:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run: python app.py
echo   3. Open browser: http://localhost:5000
echo.
echo Default login:
echo   Username: admin
echo   Password: admin123
echo.
echo ⚠ Remember to change the default password!
echo.
pause
