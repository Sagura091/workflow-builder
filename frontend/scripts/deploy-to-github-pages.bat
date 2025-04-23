@echo off
echo Deploying Workflow Builder to GitHub Pages...

REM Step 1: Build for GitHub Pages
echo.
echo Step 1: Building for GitHub Pages...
node scripts/build-for-github-pages.js

if %ERRORLEVEL% neq 0 (
  echo Build failed. Aborting deployment.
  exit /b 1
)

REM Step 2: Install gh-pages if not already installed
echo.
echo Step 2: Checking for gh-pages package...
call npm list gh-pages || call npm install --save-dev gh-pages

REM Step 3: Deploy to GitHub Pages
echo.
echo Step 3: Deploying to GitHub Pages...
call npx gh-pages -d build

if %ERRORLEVEL% neq 0 (
  echo Deployment failed.
  exit /b 1
)

REM Step 4: Restore the original index.js
echo.
echo Step 4: Restoring original index.js...
node scripts/restore-original-index.js

echo.
echo Deployment completed successfully!
echo Your site should be available at: https://Sagura091.github.io/workflow-builder
echo Note: It may take a few minutes for the changes to propagate.
