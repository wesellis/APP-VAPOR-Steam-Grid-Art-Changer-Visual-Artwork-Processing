@echo off
echo Installing VAPOR for Windows...
echo.
echo Copying executable to Program Files...
if not exist "%PROGRAMFILES%\VAPOR" mkdir "%PROGRAMFILES%\VAPOR"
copy "VAPOR_Windows_x64.exe" "%PROGRAMFILES%\VAPOR\VAPOR.exe"
echo.
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\VAPOR.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\VAPOR\VAPOR.exe'; $Shortcut.Save()"
echo.
echo Installation complete! You can now run VAPOR from your desktop.
pause
