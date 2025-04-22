@echo off
echo Starting Workflow Builder Backend

cd backend

:: Check if this is the first run
if not exist ".imports_fixed" (
    :: Install the backend in development mode
    echo Installing backend in development mode...
    python install_dev.py

    :: Fix all imports
    echo Fixing all imports...
    python fix_all_imports.py

    :: Create a marker file to indicate imports have been fixed
    echo. > .imports_fixed
)

:: Start the backend server
echo Starting backend server...
python run.py --host 0.0.0.0 --port 8001

pause
