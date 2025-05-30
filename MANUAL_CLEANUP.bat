@echo off
title VAPOR Build Fix - Manual Cleanup
echo.
echo   🔧 VAPOR Build Fix - Manual Cleanup
echo   =====================================
echo   Fixing permission and encoding issues
echo.

echo 🔄 Stopping any running PyInstaller processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pyinstaller.exe >nul 2>&1
timeout /t 3 >nul

echo 🧹 Removing problematic build files...
if exist vapor_windows.spec del /f /q vapor_windows.spec
if exist vapor_linux.spec del /f /q vapor_linux.spec  
if exist vapor_macos.spec del /f /q vapor_macos.spec

echo 🗑️ Cleaning build directories...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul

echo 🧽 Clearing PyInstaller cache...
if exist "%LOCALAPPDATA%\pyinstaller" rmdir /s /q "%LOCALAPPDATA%\pyinstaller" 2>nul

echo 🔄 Waiting for file locks to release...
timeout /t 5 >nul

echo.
echo ✅ Manual cleanup complete!
echo.
echo 🚀 Now you can run: BUILD_ALL_PLATFORMS.bat
echo    Or manually: python build_multiplatform.py all
echo.
pause
