@echo off
cd %~dp0
call venv\Scripts\activate
set /p server_ip=<server_ip.txt
python analisys.py %server_ip% shutdown
shutdown /s /t 0