import subprocess
import time

VBOXMANAGE_PATH = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
VM_NAME = "e327684c-b70c-41a1-a52e-d6afeb96ee56"
SNAPSHOT_NAME = "analise_de_malwares_3"
TIMEOUT = 5

while True:
    # Restaurando VM
    subprocess.run([VBOXMANAGE_PATH, "snapshot", VM_NAME, "restore", SNAPSHOT_NAME], shell=True)

    # Iniciando VM
    subprocess.run([VBOXMANAGE_PATH, "startvm", VM_NAME], shell=True)

    # Verificando o estado da VM
    while True:
        vm_info = subprocess.check_output([VBOXMANAGE_PATH, "showvminfo", VM_NAME, "--machinereadable"]).decode("utf-8")
        vm_state_line = [line for line in vm_info.splitlines() if line.startswith("VMState=")][0]
        vm_state = vm_state_line.split("=", 1)[1].replace('"', '')

        if vm_state == "poweroff":
            print("A VM foi encerrada.")
            break

        time.sleep(TIMEOUT)
