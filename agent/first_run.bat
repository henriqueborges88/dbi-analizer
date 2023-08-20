@echo off
set "analisysScript=%~dp0run_agent.bat"
schtasks /create /sc onlogon /tn "RunAnalisys" /tr "%analisysScript%" /rl highest /f
exi