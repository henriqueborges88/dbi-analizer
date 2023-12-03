# analysis.py
import time
from controllers.config_controller import get_config_item
from virtualbox_manager import (configure_hostonly_network, configure_vm_hostonly_network,
                                restore_vm_snapshot, start_vm, poweroff_vm, get_vm_state)

TIMEOUT = 5

def run_analysis(flask_app, server_ip_address):
    with flask_app.app_context():
        while True:
            try:
                analysis_enabled = get_config_item("analysis_enabled")
                if analysis_enabled != "1":
                    time.sleep(1)
                    continue

                vm_name = get_config_item("vm_name")
                if not vm_name:
                    time.sleep(1)
                    continue

                snapshot_name = get_config_item("snapshot_name")
                if not snapshot_name:
                    time.sleep(1)
                    continue

                # Restaurando VM
                restore_vm_snapshot(vm_name, snapshot_name)

                # Configurando a rede host-only
                interface_name = configure_hostonly_network(server_ip_address)
                configure_vm_hostonly_network(vm_name, interface_name)
                
                # Pequena pausa para garantir que a VM esteja pronta
                time.sleep(2)

                # Iniciando VM
                start_vm(vm_name)

                max_execution_time = 900  # 15 minutos em segundos
                start_time = time.time()

                while True:
                    vm_state = get_vm_state(vm_name)

                    if vm_state == "poweroff":
                        break

                    current_time = time.time()
                    execution_time = current_time - start_time

                    if execution_time > max_execution_time:
                        print(f"O tempo máximo de execução foi alcançãdo. Interrompendo a VM {vm_name}")
                        poweroff_vm(vm_name)
                        # Pequena pausa após desligar a VM
                        time.sleep(5)

                    time.sleep(TIMEOUT)
            except Exception as e:
                print(f"An error occurred: {e}")
