@echo off
setlocal
cd /d "%~dp0" || exit /b 1
python -m venv venv
if errorlevel 1 exit /b 1
call venv\Scripts\activate.bat
if errorlevel 1 exit /b 1
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
python app.py
exit /b %errorlevel%
