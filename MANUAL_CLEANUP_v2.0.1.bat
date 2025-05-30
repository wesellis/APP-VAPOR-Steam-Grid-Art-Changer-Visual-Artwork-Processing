@echo off
echo 🧹 VAPOR v2.0.1 - Manual Cleanup Script
echo ========================================
echo Forcefully cleaning build artifacts for v2.0.1 release...
echo.

echo 🔄 Terminating any hanging PyInstaller processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im pyinstaller.exe 2>nul
timeout /t 3 /nobreak >nul

echo 🗑️ Removing build directories...
if exist "A:\GITHUB\VAPOR\build" (
    echo Removing build directory...
    rmdir /s /q "A:\GITHUB\VAPOR\build" 2>nul
    timeout /t 2 /nobreak >nul
)

if exist "A:\GITHUB\VAPOR\dist" (
    echo Removing dist directory...
    rmdir /s /q "A:\GITHUB\VAPOR\dist" 2>nul
    timeout /t 2 /nobreak >nul
)

echo 🧹 Removing spec files...
del "A:\GITHUB\VAPOR\*.spec" 2>nul

echo 🗂️ Clearing PyInstaller cache...
rmdir /s /q "%LOCALAPPDATA%\pyinstaller" 2>nul
rmdir /s /q "%TEMP%\pyinstaller" 2>nul

echo ⏳ Waiting for file locks to release...
timeout /t 5 /nobreak >nul

echo ✅ Cleanup complete! Ready for v2.0.1 build.
echo.
echo Next step: Run BUILD_v2.0.1.bat
pause
