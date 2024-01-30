
# Before You Begin

## Setting Up virtual environment
``` python -m venv venv ```

## Activate the virtual environment
``` source venv/bin/activate ```

## Install requirements 
Install libraries using ``` pip install <library> ``` 
Install Libraries from a file - ``` pip install -r requirements.txt```

## Save requirements 
After you install libraries using ```pip```, save them to the ```requirements.txt``` file using 
 ``` pip freeze > requirements.txt ```

## Set Up Django Project
``` django-admin startproject <project_name>```
If you want the project to be in the same directory, use  ``` django-admin startproject <project_name> .```

## Start a django app
``` python manage.py startapp <app_name>```

## Run
``` python manage.py runserver```