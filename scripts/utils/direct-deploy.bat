@echo off
echo Directly deploying Workflow Builder to GitHub Pages...
echo.

REM Step 1: Install dependencies
echo Step 1: Installing dependencies...
call npm install --save-dev gh-pages --legacy-peer-deps

REM Step 2: Build the application
echo.
echo Step 2: Building the application...
call npx react-scripts build --legacy-peer-deps

REM Step 3: Deploy to GitHub Pages
echo.
echo Step 3: Deploying to GitHub Pages...
call npx gh-pages -d build

echo.
echo Deployment process completed!
echo Your site should be available at: https://Sagura091.github.io/workflow-builder
echo Note: It may take a few minutes for the changes to propagate.
pause
