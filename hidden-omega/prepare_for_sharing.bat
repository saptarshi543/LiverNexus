@echo off
echo ===================================================
echo   LIVERNEXUS SHARING PREPARATION TOOL
echo ===================================================
echo.
echo This script will DELETE the 'node_modules' and 'backend/venv' folders.
echo This reduces the project size significantly (from ~500MB to ~5MB)
echo so you can easily ZIP and email/upload it.
echo.
echo NOTE: The next person will need to run 'npm install' and reinstall python requirements.
echo.
pause

echo.
echo Deleting node_modules...
rmdir /s /q frontend\node_modules
echo Deleting Python venv...
rmdir /s /q backend\venv

echo.
echo cleanup Complete! You can now ZIP the 'hidden-omega' folder.
pause
