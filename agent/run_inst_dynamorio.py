import json
import os
import re
from subprocess import Popen, getoutput, PIPE, STDOUT
from time import sleep
from utils import wait_until_finish, instr_proc_task_kill, proc_kill_force

def run_dynamorio(file, architecture, out_dir):
    print("Executando Dynamorio")
    
    out_dir = os.path.join(out_dir, "dynamorio")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    dynamorio_run_data_path = os.path.join(out_dir, "dynamorio_run_data.txt")
    dynamorio_stderr_path = os.path.join(out_dir, 'dynamorio_stderr.txt')
    dynamorio_stdout_path = os.path.join(out_dir, 'dynamorio_stdout.txt')
    if architecture == "32 bits":
        dynamorio_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin32/drrun.exe")
        drkill_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin32/DRkill.exe")
    elif architecture == "64 bits":
        dynamorio_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin64/drrun.exe")
        drkill_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin64/DRkill.exe")
    else:
        raise Exception(architecture)
    
    target_file_name = os.path.basename(file)
    
    with open(dynamorio_stdout_path, 'w') as output_file, open(dynamorio_stderr_path, 'w') as error_file:
        dynamorio_proc = Popen(f"\"{dynamorio_path}\" -s 40 -exit0 -no_inject -t drcachesim -simulator_type basic_counts -- \"{file}\"", shell=True, stdout=output_file, stderr=error_file)
    
    wait_until_finish(dynamorio_proc)
    instr_proc_task_kill(target_file_name)
    instr_proc_task_kill(target_file_name, True)
    wait_until_finish(dynamorio_proc, timeout=5)
    proc_kill_force(dynamorio_proc)
    Popen(f"\"{drkill_path}\" -underdr", shell=True, stdout=PIPE, stderr=PIPE)
    
       
    with open(dynamorio_stderr_path, 'r') as file:
        text = file.read()

    if "Basic counts tool results:" in text:
        dynamorio_tool_success = True

    try:
        returncode = dynamorio_proc.returncode
    except:
        returncode = 2032 # Erro ao obter o returncode do instrumentador

    dynamorio_dict = {
        "dynamorio_returncode": returncode,
        "dynamorio_tool_success": dynamorio_tool_success
    }

    print("[dynamorio] Instrumentaçao concluida")

    with open(dynamorio_run_data_path, 'w') as json_file:
        json.dump(dynamorio_dict, json_file, sort_keys=False, indent=4)
