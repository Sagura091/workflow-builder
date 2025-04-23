@echo off
echo Starting standalone demo update...

REM Run the PowerShell update script
powershell -ExecutionPolicy Bypass -File "%~dp0\update-standalone-demo.ps1"

if %ERRORLEVEL% EQU 0 (
    echo Update completed successfully!
) else (
    echo Update failed with error code %ERRORLEVEL%
)

pause
