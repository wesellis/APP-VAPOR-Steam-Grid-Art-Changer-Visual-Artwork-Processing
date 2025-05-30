@echo off
echo 🔧 Quick Icon Fix for VAPOR
echo =============================
echo Copying assets to builds directory so executable can find them...
echo.

cd /d "A:\GITHUB\VAPOR"

echo 📁 Creating assets folder in builds...
if not exist "builds\assets" mkdir "builds\assets"

echo 📋 Copying icon and logo files...
if exist "assets\Vapor_Icon.png" (
    copy "assets\Vapor_Icon.png" "builds\assets\"
    copy "assets\Vapor_Icon.png" "builds\"
    echo ✅ Copied Vapor_Icon.png
) else (
    echo ❌ assets\Vapor_Icon.png not found
)

if exist "assets\Vapor_Logo.png" (
    copy "assets\Vapor_Logo.png" "builds\assets\"
    copy "assets\Vapor_Logo.png" "builds\"
    echo ✅ Copied Vapor_Logo.png
) else (
    echo ❌ assets\Vapor_Logo.png not found
)

echo.
echo 🎯 Now testing executable with icon...
cd builds
if exist "VAPOR_Windows_v2.0.1.exe" (
    echo Starting VAPOR to test icon...
    start VAPOR_Windows_v2.0.1.exe
    echo.
    echo 👀 Check if the icon appears in:
    echo   • Window title bar
    echo   • Taskbar
    echo   • Application header
) else (
    echo ❌ VAPOR_Windows_v2.0.1.exe not found in builds directory
)

echo.
pause
