@echo off
echo 🎨 VAPOR Multi-Platform Build System
echo Creating executables for Windows, macOS, Linux, and Steam Deck
echo.

echo 🔧 Cleaning up previous build artifacts...
python fix_build_issues.py

echo.
echo 🔧 Installing/updating build dependencies...
pip install --upgrade pyinstaller pillow requests

echo.
echo 🚀 Starting multi-platform build process...
python build_multiplatform.py all

echo.
echo ✅ Build process complete! Check the 'builds' folder for all executables.
pause
