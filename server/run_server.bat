@echo off
call venv\Scripts\activate
pip install -r requirements.txt
flask run --host 0.0.0.0