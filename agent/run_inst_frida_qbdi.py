import os
import sys
from utils import wait_until_finish, instr_proc_task_kill, proc_kill_force
import frida
import subprocess
import json
import re
from subprocess import Popen, getoutput, PIPE, STDOUT
from time import sleep


def run_frida():
    file = "C:\\Users\\henri\\OneDrive\\Documentos\\GitHub\\dbi-analizer\\agent\\in\\pendmoves64.exe"
    instrumentation_errors = []
    functions_user32 = []

    frida_tool_path = "C:\\Users\\henri\\OneDrive\\Documentos\\GitHub\\frida-qbdi\\qbdi.js" #os.path.abspath("./tools/frida/qbdi.js") # ilenmix

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
        print("message -> ", message)
        if message['type'] == 'send':
            functions_user32.append(json.loads(message['payload']))
        elif message['type'] == 'error':
            instrumentation_errors.append(message['description'])

    script.on('message', on_message)
    script.on("destroyed", on_destroyed)
    # Inicializa o script
    script.load()
 
    wait_until_finish(sample_proc, timeout=60)
    sample_proc.terminate()
    sleep(1)
    
    instr_proc_task_kill(file_name)
    instr_proc_task_kill(file_name, True)
    proc_kill_force(sample_proc)

    session.detach()

run_frida()