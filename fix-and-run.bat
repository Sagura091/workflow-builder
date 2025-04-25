@echo off
echo Fixing dependencies and running the workflow builder...

REM Remove node_modules and package-lock.json
echo Removing existing node_modules and package-lock.json...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

REM Install specific versions of problematic dependencies
echo Installing specific versions of dependencies...
call npm install --save ajv@8.12.0
call npm install --save ajv-keywords@5.1.0

REM Install all dependencies
echo Installing all dependencies...
call npm install

REM Start the application
echo Starting the application...
cd frontend
call npm start

pause
