@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

set /p server_ip=<server_ip.txt

python analisys.py %server_ip%