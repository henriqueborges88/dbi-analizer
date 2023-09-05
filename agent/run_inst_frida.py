import os
import sys
from utils import wait_until_finish, instr_proc_task_kill, proc_kill_force
import frida
import subprocess
import json
import re
from subprocess import Popen, getoutput, PIPE, STDOUT
from time import sleep


def run_frida(file, out):
    print("Executando Frida")

    out_dir = os.path.join(out, "frida")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    out_path = os.path.join(out_dir, "frida.json")

    instrumentation_errors = []
    functions_user32 = []

    frida_tool_path = os.path.abspath("./tools/frida/exports_user32.js") 

    file_name = os.path.basename(file)
    sample_proc = Popen(f"{file}", shell=True, stdout=PIPE, stderr=PIPE)
    sleep(2)
    try:
        session = frida.attach(sample_proc.pid)
    except frida.ProcessNotFoundError:
        print("Processo não encontrado. Certifique-se de que o processo esteja em execução.")
        return

    with open(frida_tool_path, "r") as file:
        script_code = file.read()
    script = session.create_script(script_code)

    # Cria um script Frida
    script = session.create_script(script_code)

    def on_destroyed(reason):
        print("Script finalizou:", reason)

    def on_message(message, data):
        if message['type'] == 'send':
            functions_user32.append(json.loads(message['payload']))
        elif message['type'] == 'error':
            instrumentation_errors.append(message['description'])

    script.on('message', on_message)
    script.on("destroyed", on_destroyed)
    # Inicializa o script
    script.load()
    
    wait_until_finish(sample_proc, timeout=5)
    sample_proc.terminate()
    sleep(1)
    
    instr_proc_task_kill(file_name)
    instr_proc_task_kill(file_name, True)
    proc_kill_force(sample_proc)
    
    session.detach()

    try:
        sample_out, sample_error = sample_proc.communicate()
        sample_out = sample_out.decode(errors='replace')
        sample_error = sample_error.decode(errors='replace')
        
        frida_dict = {
            "stdout": sample_out,
            "stderror": sample_error,
            "returncode": sample_proc.returncode,
            "has_error": sample_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
            "functions_user32": functions_user32,
            "instrumentation_errors": instrumentation_errors
        }
    except Exception as ex:
        frida_dict = {
            "stdout": "Tempo limite esgotado",
            "stderror": sample_error,
            "returncode": sample_proc.returncode,
            "has_error": sample_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
            "functions_user32": functions_user32,
            "instrumentation_errors": instrumentation_errors
        }

    with open(out_path, 'w') as json_file:
        json.dump(frida_dict, json_file, sort_keys=False, indent=4)