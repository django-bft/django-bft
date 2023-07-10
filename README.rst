.. django-bft - A Big File Transfer App Written in Django documentation master file, created by
   sphinx-quickstart on Thu Apr 14 11:03:55 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-bft - documentation
=====================================

Introduction
------------

**django-bft** is a Django application that handles large file transfers.  The
application's frontend has both a flash upload as well as a javascript 
upload version.

**django-bft** was origianlly created for Utah State University 
to fulfill a specific need of sending large files through email.

The site can be viewed at https://bft.usu.edu

Requirements
------------

- Django4.x
- Postgres and/or sqlite3
- Docker (if using postgres, recommended in production)
- Poetry
- Python3.9 or higher
	

Installation
------------
1. Clone the repo
2. Install requirements
3. Create a virtual environment - 'poetry shell'
4. Create a '.env' file from '.env.example', fill out blank fields.
   * SECRET_KEY can be created with python:
        ```
        import secrets
        print(secrets.token_urlsafe(15))
        ```

5. Run 'poetry install' to install dependencies
6. Run 'python manage.py migrate' to create database tables

IF USING DOCKER + postgres (recommended in production)
7. Run 'docker compose up --build'

IF RUNNING LOCALLY WITH sqlite3
7. Run 'python manage.py runserver'
	
__ https://github.com/django-bft/dango-bft/downloads
