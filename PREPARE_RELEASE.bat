@echo off
echo.
echo =============================================
echo    VAPOR - GitHub Release Preparation
echo =============================================
echo.

echo 📸 Copying screenshots...
copy "..\screenshots\*" "screenshots\" >nul 2>&1
if exist "screenshots\Auto-Enhancing.png" (
    echo ✅ Screenshots copied successfully
) else (
    echo ❌ Screenshot copy failed - please copy manually
    echo    From: ..\screenshots\
    echo    To: screenshots\
)

echo.
echo 🖼️ Copying logo...
copy "..\Vapor_Logo.png" "." >nul 2>&1
if exist "Vapor_Logo.png" (
    echo ✅ Logo copied successfully
) else (
    echo ❌ Logo copy failed - please copy manually
    echo    From: ..\Vapor_Logo.png
    echo    To: current folder
)

echo.
echo 📦 Copying executable...
copy "..\dist\VAPOR_v2.0.0.exe" "." >nul 2>&1
if exist "VAPOR_v2.0.0.exe" (
    echo ✅ Executable copied successfully
    for %%A in (VAPOR_v2.0.0.exe) do echo    Size: %%~zA bytes
) else (
    echo ❌ Executable copy failed - please copy manually
    echo    From: ..\dist\VAPOR_v2.0.0.exe
    echo    To: current folder
)

echo.
echo 🎉 GitHub release package ready!
echo.
echo 📁 Contents:
echo    ✅ README.md (amazing GitHub homepage)
echo    ✅ LICENSE (MIT license)
echo    ✅ .gitignore (clean repository)
echo    ✅ requirements.txt (Python dependencies)
echo    ✅ RELEASE_NOTES.md (version changelog)
echo    ✅ screenshots/ (UI images)
echo    ✅ VAPOR_v2.0.0.exe (standalone executable)
echo    ✅ docs/GITHUB_SETUP_GUIDE.md (complete instructions)
echo.
echo 🌟 Ready to upload to GitHub!
echo    1. Create new repository on GitHub
echo    2. Upload all these files
echo    3. Create release with VAPOR_v2.0.0.exe attached
echo    4. Share on gaming subreddits
echo    5. Watch it go viral! 🚀
echo.
pause
