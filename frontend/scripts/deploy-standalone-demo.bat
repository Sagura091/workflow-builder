@echo off
echo Starting standalone demo deployment...

REM Run the PowerShell deployment script
powershell -ExecutionPolicy Bypass -File "%~dp0\deploy-standalone-demo.ps1"

if %ERRORLEVEL% EQU 0 (
    echo Deployment completed successfully!
) else (
    echo Deployment failed with error code %ERRORLEVEL%
)

pause
