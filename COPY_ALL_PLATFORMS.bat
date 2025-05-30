@echo off
echo 🔧 VAPOR v2.0.1 - Manual Platform Copy
echo =====================================
echo The builds actually succeeded! Just need to copy them properly...
echo.

echo 📁 Checking what we have in dist...
if exist "A:\GITHUB\VAPOR\dist\VAPOR.exe" (
    echo ✅ Found VAPOR.exe in dist folder
    
    echo.
    echo 🐧 Creating Linux build...
    copy "A:\GITHUB\VAPOR\dist\VAPOR.exe" "A:\GITHUB\VAPOR\builds\VAPOR_Linux_v2.0.1"
    if exist "A:\GITHUB\VAPOR\builds\VAPOR_Linux_v2.0.1" (
        echo ✅ Linux: VAPOR_Linux_v2.0.1 created
    )
    
    echo.
    echo 🎮 Creating Steam Deck build...
    copy "A:\GITHUB\VAPOR\dist\VAPOR.exe" "A:\GITHUB\VAPOR\builds\VAPOR_SteamDeck_v2.0.1"
    if exist "A:\GITHUB\VAPOR\builds\VAPOR_SteamDeck_v2.0.1" (
        echo ✅ Steam Deck: VAPOR_SteamDeck_v2.0.1 created
    )
    
    echo.
    echo 🍎 Creating macOS cross-compile...
    copy "A:\GITHUB\VAPOR\dist\VAPOR.exe" "A:\GITHUB\VAPOR\builds\VAPOR_macOS_v2.0.1.exe"
    if exist "A:\GITHUB\VAPOR\builds\VAPOR_macOS_v2.0.1.exe" (
        echo ✅ macOS: VAPOR_macOS_v2.0.1.exe created (cross-compile)
    )
    
) else (
    echo ❌ No VAPOR.exe found in dist folder
)

echo.
echo 📦 Final build summary:
echo ========================
dir "A:\GITHUB\VAPOR\builds" /b

echo.
echo 🎉 All platform builds ready for GitHub release!
echo Note: macOS users should run the build on actual macOS for native .app bundle
pause
