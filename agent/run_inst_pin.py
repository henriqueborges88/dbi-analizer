import json
import os
import re
from subprocess import Popen, getoutput, PIPE, STDOUT
from time import sleep
from utils import wait_until_finish, instr_proc_task_kill, instr_proc_task_kill_force, proc_kill_force

def run_pin(file, out):
    # if "RDCMan" not in file: 
    #     return
    pin_path = os.path.abspath("./tools/pin-3.28-msvc-windows/pin.exe")
    pin_tool_path = os.path.abspath("./tools/pin-3.28-msvc-windows/source/tools/SimpleExamples/obj-intel64/icount.dll") # ilenmix

    file_name = os.path.basename(file)
    
    pin_proc = Popen(f"\"{pin_path}\" -t \"{pin_tool_path}\" -- \"{file}\"", shell=True, stdout=PIPE, stderr=PIPE)
    pin_wait_secconds = 0
    while pin_proc.poll() is None and pin_wait_secconds < 30:
        pin_wait_secconds +=1
        sleep(1)

    wait_until_finish(pin_proc)
    instr_proc_task_kill(pin_proc, file_name)
    instr_proc_task_kill_force(pin_proc, file_name)
    wait_until_finish(pin_proc, timeout=5)
    proc_kill_force(pin_proc)

    try:
        pin_out, pin_error = pin_proc.communicate()
        pin_out = pin_out.decode(errors='replace')
        pin_error = pin_error.decode(errors='replace')

        i_count = 0
        p_count = r'Count (\d+)$'
        match = re.search(p_count, pin_error)
        if match:
            i_count = match.group(1)
            pin_error = pin_error.replace(match.string, "").strip()

        pin_dict = {
            "pin_stdout": pin_out,
            "pin_stderror": pin_error,
            "pin_returncode": pin_proc.returncode,
            "pin_has_error": pin_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
            "pin_intructions_count": i_count
        }
    except Exception as ex:
        pin_dict = {
            "pin_stdout": "Tempo limite esgotado",
            "pin_stderror": pin_error,
            "pin_returncode": pin_proc.returncode,
            "pin_has_error": pin_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
            "pin_intructions_count": 0
        }

    print("[Pin] Instrumentaçao concluida")

    with open(out, 'w') as json_file:
        json.dump(pin_dict, json_file, sort_keys=False, indent=4)
