import subprocess
import time
from database import get_config

VBOXMANAGE_PATH = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
TIMEOUT = 2

def run_analisys():
    while True:
        try:
            analysis_enabled = get_config("analysis_enabled")
            if analysis_enabled != "1":
                time.sleep(1)
                continue
            
            vm_name = get_config("vm_name")
            if not vm_name:
                time.sleep(1)
                continue

            snapshot_name = get_config("snapshot_name")
            if not snapshot_name:
                time.sleep(1)
                continue

            # Restaurando VM
            subprocess.run([VBOXMANAGE_PATH, "snapshot", vm_name, "restore", snapshot_name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Iniciando VM
            subprocess.run([VBOXMANAGE_PATH, "startvm", vm_name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            max_execution_time = 900  # 15 minutos em segundos
            start_time = time.time()  

            while True:
                vm_info = subprocess.check_output([VBOXMANAGE_PATH, "showvminfo", vm_name, "--machinereadable"]).decode("utf-8")
                vm_state_line = [line for line in vm_info.splitlines() if line.startswith("VMState=")][0]
                vm_state = vm_state_line.split("=", 1)[1].replace('"', '')

                if vm_state == "poweroff":
                    break

                current_time = time.time()
                execution_time = current_time - start_time

                if execution_time > max_execution_time:
                    subprocess.run([VBOXMANAGE_PATH, "controlvm", vm_name, "poweroff"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                time.sleep(TIMEOUT)
        except:
            pass