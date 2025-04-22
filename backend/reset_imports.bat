@echo off
echo Resetting imports marker...

:: Remove the imports_fixed marker file
if exist ".imports_fixed" (
    del /f /q .imports_fixed
    echo Imports marker removed. The next time you run the backend, imports will be fixed again.
) else (
    echo No imports marker found. Nothing to reset.
)

pause
