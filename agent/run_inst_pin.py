import json
import os
import re
from subprocess import Popen, getoutput, PIPE, STDOUT
from time import sleep
from utils import wait_until_finish, instr_proc_task_kill, instr_proc_task_kill_force, proc_kill_force

def run_pin(file, architecture, out_dir):
    pin_out_path = os.path.join(out_dir, "pin_out.txt")
    pin_log_path = os.path.join(out_dir, "pin_log.txt")
    pin_error_file = os.path.join(out_dir, "pin_error.txt")
    pintool_out = os.path.join(out_dir, "pintool_out.txt")
    file_name = os.path.basename(file)
    pintool = "inscount2_mt.dll"
    
    if architecture == "32 bits":
        pin_path = os.path.abspath("./tools/pin-3.28-msvc-windows/ia32/bin/pin.exe")
        pin_tool_path = os.path.abspath(f"./tools/pin-3.28-msvc-windows/source/tools/SimpleExamples/obj-ia32/{pintool}") # ilenmix
    elif architecture == "64 bits":
        pin_path = os.path.abspath("./tools/pin-3.28-msvc-windows/intel64/bin/pin.exe")
        pin_tool_path = os.path.abspath(f"./tools/pin-3.28-msvc-windows/source/tools/SimpleExamples/obj-intel64/{pintool}") # ilenmix
    else:
        raise Exception(architecture)
    pin_proc = Popen(f"\"{pin_path}\" -logfile \"{pin_log_path}\" -error_file \"{pin_error_file}\" -t \"{pin_tool_path}\" -o \"{pintool_out}\" -- \"{file}\"", shell=True, stdout=PIPE, stderr=PIPE)
    
    wait_until_finish(pin_proc)
    instr_proc_task_kill(pin_proc, file_name)
    instr_proc_task_kill_force(pin_proc, file_name)
    wait_until_finish(pin_proc, timeout=5)
    proc_kill_force(pin_proc)

    try:
        pin_out, pin_error = pin_proc.communicate()
        pin_out = pin_out.decode(errors='replace')
        pin_error = pin_error.decode(errors='replace')

        pin_dict = {
            "pin_stdout": pin_out,
            "pin_stderror": pin_error,
            "pin_returncode": pin_proc.returncode,
            "pin_has_error": pin_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
        }
    except Exception as ex:
        pin_dict = {
            "pin_stdout": "Tempo limite esgotado",
            "pin_stderror": pin_error,
            "pin_returncode": pin_proc.returncode,
            "pin_has_error": pin_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
        }

    print("[Pin] Instrumentaçao concluida")

    with open(pin_out_path, 'w') as json_file:
        json.dump(pin_dict, json_file, sort_keys=False, indent=4)
