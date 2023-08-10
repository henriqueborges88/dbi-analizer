@echo off
call venv\Scripts\activate
pip install -r requirements.txt
set FLASK_APP=server.py
set FLASK_ENV=test
flask run --host=0.0.0.0