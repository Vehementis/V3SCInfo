@echo off
REM Build script for V3SCInfo - Star Citizen Stats Reader
REM By V3h3m3ntis for the Hiv3mind Community
REM This script creates a standalone executable using PyInstaller

echo Building V3SCInfo - Star Citizen Stats Reader...
echo ==============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available
    echo Please ensure pip is installed
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build the executable
echo Building executable...
python -m PyInstaller build.spec --clean --noconfirm
if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

REM Check if build was successful
if exist "dist\V3SCInfo.exe" (
    echo.
    echo Build completed successfully!
    echo Executable created: dist\V3SCInfo.exe
    echo.
    echo You can now distribute this single file to run V3SCInfo
    echo without requiring Python installation.
    echo.
    echo Created by V3h3m3ntis for the Hiv3mind Community!
    echo.
    
    REM Optional: Test the executable
    echo Testing the executable...
    "dist\V3SCInfo.exe" --help
    
) else (
    echo Error: Executable was not created
    pause
    exit /b 1
)

echo.
echo Build process completed.
pause
