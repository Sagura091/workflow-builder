@echo off
echo Deploying Workflow Builder Demo to GitHub Pages...
echo.

echo Step 1: Installing dependencies...
echo Using --legacy-peer-deps to resolve TypeScript version conflicts
call npm install --legacy-peer-deps
if %ERRORLEVEL% NEQ 0 (
    echo Error installing dependencies. Please check your npm installation.
    pause
    exit /b 1
)

echo.
echo Step 2: Building and deploying the application...
call npm run deploy
if %ERRORLEVEL% NEQ 0 (
    echo Error deploying the application. Please check the error messages above.
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
