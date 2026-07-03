@echo off
echo Starting TravelGo Django Backend...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python manage.py runserver
pause
