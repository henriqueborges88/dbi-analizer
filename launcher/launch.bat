@echo off
cd "C:\Program Files\Oracle\VirtualBox"
set VM_NAME="e327684c-b70c-41a1-a52e-d6afeb96ee56"
set SNAPSHOT_NAME="analise_de_malwares"
set TIMEOUT=5

:loop
rem Restaurando VM
VBoxManage snapshot "%VM_NAME%" restore "%SNAPSHOT_NAME%"

rem Iniciando VM
VBoxManage startvm "%VM_NAME%"

:CHECK_VM_STATE
for /f "tokens=2 delims== " %%a in ('VBoxManage showvminfo "%VM_NAME%" --machinereadable ^| find "VMState="') do (
    set "VM_STATE=%%~a"
)

if "%VM_STATE%"=="poweroff" (
    echo A VM foi encerrada.
) else (
    timeout /t %TIMEOUT% /nobreak > nul
    goto CHECK_VM_STATE
)

goto loop

