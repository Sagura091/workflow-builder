@echo off
echo Deploying Workflow Builder to GitHub Pages...
echo.

REM Step 1: Update package.json
echo Step 1: Updating package.json with new scripts...
copy package.json package.json.backup
copy package.json.new package.json

REM Step 2: Install dependencies
echo.
echo Step 2: Installing dependencies...
call npm install --save-dev gh-pages --legacy-peer-deps

REM Step 3: Build and deploy
echo.
echo Step 3: Building and deploying to GitHub Pages...
call npm run build:github

echo.
echo Deployment process completed!
echo Your site should be available at: https://Sagura091.github.io/workflow-builder
echo Note: It may take a few minutes for the changes to propagate.
pause
