@echo off
echo Fixing DemoModeContext issues...
echo.

REM Step 1: Update DemoModeContext.tsx
echo Step 1: Updating DemoModeContext.tsx...
copy frontend\src\contexts\DemoModeContext.tsx frontend\src\contexts\DemoModeContext.tsx.backup
copy DemoModeContext.tsx frontend\src\contexts\DemoModeContext.tsx

REM Step 2: Update WorkflowBuilderWrapper.tsx
echo.
echo Step 2: Updating WorkflowBuilderWrapper.tsx...
copy frontend\src\components\WorkflowBuilder\WorkflowBuilderWrapper.tsx frontend\src\components\WorkflowBuilder\WorkflowBuilderWrapper.tsx.backup
mkdir -p frontend\src\components\WorkflowBuilder
copy components\WorkflowBuilder\WorkflowBuilderWrapper.tsx frontend\src\components\WorkflowBuilder\WorkflowBuilderWrapper.tsx

REM Step 3: Add GithubPagesEntry.tsx
echo.
echo Step 3: Adding GithubPagesEntry.tsx...
copy GithubPagesEntry.tsx frontend\src\GithubPagesEntry.tsx

echo.
echo Files updated successfully!
echo Now you can run the deployment script.
pause
