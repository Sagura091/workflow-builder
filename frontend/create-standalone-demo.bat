@echo off
echo Creating standalone demo HTML file...
echo.

echo Step 1: Installing dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo Error installing dependencies. Please check your npm installation.
    pause
    exit /b 1
)

echo.
echo Step 2: Building and bundling the application...
call npm run create-standalone
if %ERRORLEVEL% NEQ 0 (
    echo Error building the application. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Step 3: Copying the file to the root directory...
if not exist build\workflow-builder-demo.html (
    echo Error: The standalone HTML file was not created.
    pause
    exit /b 1
)

copy build\workflow-builder-demo.html .
if %ERRORLEVEL% NEQ 0 (
    echo Error copying the file. Please check if you have write permissions.
    pause
    exit /b 1
)

echo.
echo Standalone demo created successfully!
echo You can now open workflow-builder-demo.html in any browser.
echo.

echo Would you like to open the demo now? (Y/N)
set /p OPEN_DEMO=
if /i "%OPEN_DEMO%"=="Y" (
    start workflow-builder-demo.html
)

pause
