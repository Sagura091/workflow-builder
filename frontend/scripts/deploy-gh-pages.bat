@echo off
echo Starting GitHub Pages deployment...

REM Run the PowerShell deployment script
powershell -ExecutionPolicy Bypass -File "%~dp0\deploy-gh-pages.ps1"

if %ERRORLEVEL% EQU 0 (
    echo Deployment completed successfully!
) else (
    echo Deployment failed with error code %ERRORLEVEL%
)

pause
