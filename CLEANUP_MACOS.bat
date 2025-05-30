@echo off
echo 🧹 Cleaning up invalid macOS .exe file...
echo.

if exist "A:\GITHUB\VAPOR\builds\VAPOR_macOS_v2.0.1.exe" (
    echo Removing VAPOR_macOS_v2.0.1.exe (won't work on macOS anyway)
    del "A:\GITHUB\VAPOR\builds\VAPOR_macOS_v2.0.1.exe"
    echo ✅ Removed invalid macOS .exe file
) else (
    echo ℹ️ No macOS .exe file found
)

echo.
echo 📦 Final 3-Platform Build Summary:
echo ==================================
dir "A:\GITHUB\VAPOR\builds" /b

echo.
echo 🎯 Ready for GitHub release with 3 platforms:
echo • Windows: VAPOR_Windows_v2.0.1.exe
echo • Linux: VAPOR_Linux_v2.0.1  
echo • Steam Deck: VAPOR_SteamDeck_v2.0.1
echo • macOS: Coming in future release (needs native Mac build)
echo.
pause
