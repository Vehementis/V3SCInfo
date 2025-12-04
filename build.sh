#!/bin/bash
# Build script for V3SCInfo on Linux/Mac
# This script creates a standalone executable using PyInstaller

echo "Building V3SCInfo..."
echo "====================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not available"
    echo "Please ensure pip is installed"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist build

# Build the executable
echo "Building executable..."
python3 -m PyInstaller build.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "Error: Build failed"
    exit 1
fi

# Check if build was successful
if [ -f "dist/V3SCInfo" ]; then
    echo ""
    echo "Build completed successfully!"
    echo "Executable created: dist/V3SCInfo"
    echo ""
    echo "You can now distribute this single file to run the application"
    echo "without requiring Python installation."
    echo ""
    
    # Make executable
    chmod +x "dist/V3SCInfo"
    
    # Optional: Test the executable
    echo "Testing the executable..."
    "./dist/V3SCInfo" --help
    
else
    echo "Error: Executable was not created"
    exit 1
fi

echo ""
echo "Build process completed."
