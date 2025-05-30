@echo off
echo 🌍 VAPOR v2.0.1 - COMPLETE MULTI-PLATFORM BUILD
echo ===============================================
echo Building for Windows, Linux, macOS, and Steam Deck
echo.

echo 🧹 STEP 1: AGGRESSIVE CLEANUP
echo Terminating ALL Python processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
timeout /t 3 /nobreak >nul

echo Removing ALL build artifacts...
rmdir /s /q "A:\GITHUB\VAPOR\build" 2>nul
rmdir /s /q "A:\GITHUB\VAPOR\dist" 2>nul
del "A:\GITHUB\VAPOR\*.spec" 2>nul
rmdir /s /q "%LOCALAPPDATA%\pyinstaller" 2>nul
rmdir /s /q "%TEMP%\pyinstaller" 2>nul

echo Waiting for filesystem to stabilize...
timeout /t 5 /nobreak >nul

echo ✅ Cleanup complete!
echo.

echo 🚀 STEP 2: BUILDING INDIVIDUAL PLATFORMS
echo Building each platform separately to avoid conflicts...
echo.

echo 🪟 Building Windows v2.0.1...
python build_multiplatform.py windows
if exist "A:\GITHUB\VAPOR\builds\VAPOR_Windows_v2.0.1.exe" (
    echo ✅ Windows build successful!
) else (
    echo ❌ Windows build failed
)
echo.

echo 🧹 Cleaning between builds...
rmdir /s /q "A:\GITHUB\VAPOR\build" 2>nul
rmdir /s /q "A:\GITHUB\VAPOR\dist" 2>nul
timeout /t 3 /nobreak >nul

echo 🐧 Building Linux v2.0.1...
python build_multiplatform.py linux
if exist "A:\GITHUB\VAPOR\builds\VAPOR_Linux_v2.0.1" (
    echo ✅ Linux build successful!
) else (
    echo ❌ Linux build failed
)
echo.

echo 🧹 Cleaning between builds...
rmdir /s /q "A:\GITHUB\VAPOR\build" 2>nul
rmdir /s /q "A:\GITHUB\VAPOR\dist" 2>nul
timeout /t 3 /nobreak >nul

echo 🎮 Building Steam Deck v2.0.1...
python build_multiplatform.py steamdeck
if exist "A:\GITHUB\VAPOR\builds\VAPOR_SteamDeck_v2.0.1" (
    echo ✅ Steam Deck build successful!
) else (
    echo ❌ Steam Deck build failed
)
echo.

echo 🧹 Cleaning between builds...
rmdir /s /q "A:\GITHUB\VAPOR\build" 2>nul
rmdir /s /q "A:\GITHUB\VAPOR\dist" 2>nul
timeout /t 3 /nobreak >nul

echo 🍎 Building macOS v2.0.1...
python build_multiplatform.py macos
if exist "A:\GITHUB\VAPOR\builds\VAPOR_macOS.app" (
    echo ✅ macOS build successful!
) else (
    echo ❌ macOS build failed
)
echo.

echo 🎯 STEP 3: CREATING RELEASE PACKAGES
echo Creating desktop files and installers...
python -c "
from build_multiplatform import VaporBuildSystem
builder = VaporBuildSystem()
builder.create_desktop_files()
builder.create_installation_scripts()
builder.create_release_packages()
"

echo.
echo 📦 STEP 4: BUILD SUMMARY
echo ========================
echo Checking what was built successfully...
echo.

if exist "A:\GITHUB\VAPOR\builds\VAPOR_Windows_v2.0.1.exe" (
    echo ✅ Windows: VAPOR_Windows_v2.0.1.exe
) else (
    echo ❌ Windows: Build failed
)

if exist "A:\GITHUB\VAPOR\builds\VAPOR_Linux_v2.0.1" (
    echo ✅ Linux: VAPOR_Linux_v2.0.1
) else (
    echo ❌ Linux: Build failed
)

if exist "A:\GITHUB\VAPOR\builds\VAPOR_SteamDeck_v2.0.1" (
    echo ✅ Steam Deck: VAPOR_SteamDeck_v2.0.1
) else (
    echo ❌ Steam Deck: Build failed
)

if exist "A:\GITHUB\VAPOR\builds\VAPOR_macOS.app" (
    echo ✅ macOS: VAPOR_macOS.app
) else (
    echo ❌ macOS: Build failed
)

echo.
echo 📁 Contents of builds directory:
dir "A:\GITHUB\VAPOR\builds" /b

echo.
echo 🎉 Multi-platform build process complete!
echo Upload ALL successful builds to GitHub release
pause
