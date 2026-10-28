@echo off
cd %~dp0
python -m venv venv
call venv\Scripts\activate
set /p server_ip=<server_ip.txt
python analysis.py %server_ip% shutdown
shutdown /s /t 0