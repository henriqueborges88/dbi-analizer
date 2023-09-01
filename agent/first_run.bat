@echo off
cd %~dp0
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

set "analisysScript=%~dp0run_agent.bat"
schtasks /create /sc onlogon /tn "RunAnalisys" /tr "%analisysScript%" /rl highest /f
pause
exit