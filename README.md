# Job Recommendation System - Environment Setup Guide

This guide will help you set up the development environment for the Job Recommendation System website project using Django, HTML, CSS, and JavaScript.

## Prerequisites

- Python 3.x installed on your system. Download from https://www.python.org/downloads/
- Basic knowledge of using the command line or terminal.

## Step 1: Create Project Directory and Virtual Environment

Open your terminal or command prompt and run the following commands:

```bash
mkdir job_recommendation_system
cd job_recommendation_system
python -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```
  source venv/bin/activate
  ```

## Step 2: Install Django

With the virtual environment activated, install Django:

```bash
pip install django
```

## Step 3: Create Django Project and App

Run the following commands to create the Django project and app:

```bash
django-admin startproject jobsite .
python manage.py startapp jobs
```

## Step 4: Configure Templates and Static Files

- Create folders named `templates` and `static` in the project root directory.
- Edit `jobsite/settings.py` to add:

```python
# In TEMPLATES setting
'DIRS': [BASE_DIR / 'templates'],

# Add static files directory
STATICFILES_DIRS = [BASE_DIR / 'static']
```

## Step 5: Run Development Server

Start the Django development server:

```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/` to see the Django welcome page.

## Testing

- Verify the server runs without errors.
- Verify the welcome page loads in the browser.
- Verify static files and templates folders are recognized by Django.

---

Follow these steps to set up your environment. Let me know if you want me to help with creating models, views, templates, or any other features.
