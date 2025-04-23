@echo off
echo Deploying Standalone Workflow Builder Demo to GitHub Pages...
echo.

REM Step 1: Install dependencies
echo Step 1: Installing dependencies...
call npm install --save-dev gh-pages --legacy-peer-deps

REM Step 2: Create a temporary build directory
echo.
echo Step 2: Creating a temporary build directory...
if exist build rmdir /s /q build
mkdir build

REM Step 3: Copy the standalone HTML file to the build directory
echo.
echo Step 3: Copying files to the build directory...
copy standalone-demo.html build\index.html

REM Step 4: Deploy to GitHub Pages
echo.
echo Step 4: Deploying to GitHub Pages...
call npx gh-pages -d build

echo.
echo Deployment process completed!
echo Your site should be available at: https://Sagura091.github.io/workflow-builder
echo Note: It may take a few minutes for the changes to propagate.
pause
