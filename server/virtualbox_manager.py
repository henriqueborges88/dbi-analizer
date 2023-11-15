import re
import subprocess
import time

VBOXMANAGE_PATH = "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe"
def list_hostonly_interfaces():
    # Lista todas as interfaces host-only existentes
    result = subprocess.run([VBOXMANAGE_PATH, "list", "hostonlyifs"], capture_output=True, text=True)
    output = result.stdout
    interfaces = re.findall(r'^Name:\s+(VirtualBox Host-Only Ethernet Adapter(?: #\d+)?|vboxnet\d+)', output, re.MULTILINE)
    return interfaces

def configure_hostonly_network(ip_address):
    print(f"Configurando adaptador de rede no modo Host-Only com o IP {ip_address}")
    interfaces = list_hostonly_interfaces()
    if interfaces:
        # Se existem interfaces, usa a primeira disponível
        interface_name = interfaces[0]
    else:
        # Se não existem, cria uma nova
        result = subprocess.run([VBOXMANAGE_PATH, "hostonlyif", "create"], capture_output=True, text=True)
        output = result.stdout
        match = re.search(r"Interface '(.+?)' was successfully created", output)
        if match:
            interface_name = match.group(1)
        else:
            raise Exception("Não foi possível criar a interface host-only ou capturar seu nome")

    # Configura o IP para a interface escolhida ou criada
    subprocess.run([VBOXMANAGE_PATH, "hostonlyif", "ipconfig", interface_name, "--ip", ip_address])
    return interface_name

def configure_vm_hostonly_network(vm_name, interface_name):
    print(f"Configurando a VM {vm_name} para usar a interface host-only {interface_name}")
    subprocess.run([VBOXMANAGE_PATH, "modifyvm", vm_name, "--nic1", "hostonly", "--hostonlyadapter1", interface_name])

def restore_vm_snapshot(vm_name, snapshot_name):
    # Restaurando VM para o snapshot especificado
    cmd_result = subprocess.run([VBOXMANAGE_PATH, "snapshot", vm_name, "restore", snapshot_name], capture_output=True)
    out_err = cmd_result.stderr.decode()
    if cmd_result.returncode != 0 and ("is already locked by a session" in out_err or "VBoxManage.exe: error: Code E_FAIL" in out_err):
        kill_vm_proc()

    return cmd_result.returncode, out_err

def start_vm(vm_name):
    # Iniciando a VM
    cmd_result = subprocess.run([VBOXMANAGE_PATH, "startvm", vm_name], capture_output=True)
    out_err = cmd_result.stderr.decode()
    if cmd_result.returncode != 0 and ("is already locked by a session" in out_err or "VBoxManage.exe: error: Code E_FAIL" in out_err):
        kill_vm_proc()

    return cmd_result.returncode, out_err

def poweroff_vm(vm_name):
    # Desligando a VM VBoxSVC.exe
    poweroff_result = subprocess.check_output([VBOXMANAGE_PATH, "controlvm", vm_name, "poweroff"]).decode("utf-8")
    if "VBoxManage.exe: error: Code E_FAIL" in poweroff_result:
        kill_vm_proc()
        subprocess.run(f"taskkill /F /IM VBoxSVC.exe > NUL 2> NUL", shell=True)
    time.sleep(5)
    # Depois de 5 seg, se o processo da VM ainda existir, ele é encerrado 
    kill_vm_proc()

def kill_vm_proc():
    subprocess.run(f"taskkill /F /IM VirtualBoxVM.exe > NUL 2> NUL", shell=True)

def get_vm_state(vm_name):
    # Obtendo o estado atual da VM
    vm_info = subprocess.check_output([VBOXMANAGE_PATH, "showvminfo", vm_name, "--machinereadable"]).decode("utf-8")
    vm_state_line = [line for line in vm_info.splitlines() if line.startswith("VMState=")][0]
    return vm_state_line.split("=", 1)[1].replace('"', '')
