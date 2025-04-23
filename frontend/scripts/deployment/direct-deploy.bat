@echo off
echo Directly deploying Workflow Builder Demo to GitHub Pages...
echo This script bypasses TypeScript version checks
echo.

echo Making sure gh-pages is installed...
call npm install --no-save --legacy-peer-deps gh-pages
if %ERRORLEVEL% NEQ 0 (
    echo Error installing gh-pages. Please check your npm installation.
    pause
    exit /b 1
)

echo.
echo Building the application...
set NODE_OPTIONS=--openssl-legacy-provider
call npx react-scripts build --legacy-peer-deps
if %ERRORLEVEL% NEQ 0 (
    echo Error building the application. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Deploying to GitHub Pages...
call npx gh-pages -d build
if %ERRORLEVEL% NEQ 0 (
    echo Error deploying to GitHub Pages. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Demo successfully deployed to GitHub Pages!
echo You can now access it at: https://Sagura091.github.io/workflow-builder
echo.
echo Note: It may take a few minutes for the changes to propagate.
echo.
pause
