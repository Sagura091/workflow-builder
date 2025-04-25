@echo off
echo Fixing dependencies for the workflow builder...

REM Remove node_modules and package-lock.json
echo Removing existing node_modules and package-lock.json...
cd ..
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

REM Install specific versions of problematic dependencies
echo Installing specific versions of dependencies...
npm install --save ajv@8.12.0
npm install --save ajv-keywords@5.1.0

REM Install all dependencies
echo Installing all dependencies...
npm install

echo Dependency fix complete! Try running npm start or npm build now.
pause
