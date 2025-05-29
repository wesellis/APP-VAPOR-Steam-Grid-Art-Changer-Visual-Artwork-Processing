@echo off
echo.
echo ========================================
echo VAPOR - Visual Artwork Processing 
echo      and Organization Resource
echo ========================================
echo.
echo Professional Steam Grid Artwork Manager
echo by Wesley Ellis - wes@wesellis.com
echo.
echo Starting VAPOR...
echo.

python steam_grid_artwork_manager.py

if errorlevel 1 (
    echo.
    echo Error occurred. Trying with python3...
    python3 steam_grid_artwork_manager.py
)

if errorlevel 1 (
    echo.
    echo Python not found or other error occurred.
    echo.
    echo Requirements:
    echo - Python 3.8 or higher
    echo - pip install requests pillow psutil
    echo.
    echo Make sure Python is installed and in your PATH.
    echo.
    pause
)
