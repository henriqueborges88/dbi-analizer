import json
import os
import re
from subprocess import Popen, getoutput, PIPE, STDOUT
from time import sleep
from utils import wait_until_finish, instr_proc_task_kill, instr_proc_task_kill_force, proc_kill_force

def run_dynamorio(file, architecture, out):
    if architecture == "32 bits":
        dynamorio_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin32/drrun.exe")
        drkill_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin32/DRkill.exe")
        dynamorio_tool_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/samples/bin32/icount.dll") 
    elif architecture == "64 bits":
        dynamorio_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin64/drrun.exe")
        drkill_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin64/DRkill.exe")
        dynamorio_tool_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/samples/bin64/icount.dll") 
    else:
        raise Exception(architecture)
    
    file_name = os.path.basename(file)
    
    dynamorio_proc = Popen(f"\"{dynamorio_path}\" -s 30 -exit0 -no_inject -t drcachesim -simulator_type basic_counts -- \"{file}\"", shell=True, stdout=PIPE, stderr=PIPE)
    
    wait_until_finish(dynamorio_proc)
    instr_proc_task_kill(dynamorio_proc, file_name)
    instr_proc_task_kill_force(dynamorio_proc, file_name)
    wait_until_finish(dynamorio_proc, timeout=5)
    proc_kill_force(dynamorio_proc)
    Popen(f"\"{drkill_path}\" -underdr", shell=True, stdout=PIPE, stderr=PIPE)
    
    try:
        dynamorio_out, dynamorio_error = dynamorio_proc.communicate()
        dynamorio_out = dynamorio_out.decode(errors='replace')
        dynamorio_error = dynamorio_error.decode(errors='replace')

        dynamorio_dict = {
            "dynamorio_stdout": dynamorio_out,
            "dynamorio_stderror": dynamorio_error,
            "dynamorio_returncode": dynamorio_proc.returncode,
            "dynamorio_has_error": dynamorio_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
        }
    except Exception as ex:
        dynamorio_dict = {
            "dynamorio_stdout": "Tempo limite esgotado",
            "dynamorio_stderror": dynamorio_error,
            "dynamorio_returncode": dynamorio_proc.returncode,
            "dynamorio_has_error": dynamorio_proc.returncode > 0 and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
        }

    print("[dynamorio] Instrumentaçao concluida")

    with open(out, 'w') as json_file:
        json.dump(dynamorio_dict, json_file, sort_keys=False, indent=4)
