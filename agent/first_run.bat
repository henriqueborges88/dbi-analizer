@echo off
cd %~dp0
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

set "analysisScript=%~dp0run_agent.bat"
schtasks /create /sc onlogon /tn "RunAnalysis" /tr "%analysisScript%" /rl highest /f

bcdedit /set hypervisorlaunchtype off

pause
exit