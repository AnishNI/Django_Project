@echo off
REM Batch script to set up Django environment for Job Recommendation System

REM Step 1: Create virtual environment
python -m venv venv

REM Step 2: Activate virtual environment
call venv\Scripts\activate.bat

REM Step 3: Install Django
pip install django

REM Step 4: Create Django project
django-admin startproject jobsite .

REM Step 5: Create Django app
python manage.py startapp jobs

echo Environment setup complete. You can now run "python manage.py runserver" to start the development server.
pause
