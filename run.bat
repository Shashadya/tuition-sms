@echo off
cd /d %~dp0
start http://localhost:8000
python manage.py runserver 0.0.0.0:8000
