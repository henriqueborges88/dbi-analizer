import json
import os
import re
from subprocess import Popen, getoutput
from time import sleep
from utils import wait_until_finish, instr_proc_task_kill, proc_kill_force

def run_pin(file, architecture, out_dir):
    pin_run_data_path = os.path.join(out_dir, "pin_run_data.txt")
    pin_log_path = os.path.join(out_dir, "pin_log.txt")
    pin_error_path = os.path.join(out_dir, "pin_error.txt")
    pintool_out_path = os.path.join(out_dir, "pintool_out.txt")
    pin_stderr_path = os.path.join(out_dir, 'pin_stderr.txt')
    pin_stdout_path = os.path.join(out_dir, 'pin_stdout.txt')
    target_file_name = os.path.basename(file)
    pintool = "inscount2_mt.dll"
    
    if architecture == "32 bits":
        pin_path = os.path.abspath("./tools/pin-3.28-msvc-windows/ia32/bin/pin.exe")
        pin_tool_path = os.path.abspath(f"./tools/pin-3.28-msvc-windows/tools/obj-ia32/{pintool}") # ilenmix
    elif architecture == "64 bits":
        pin_path = os.path.abspath("./tools/pin-3.28-msvc-windows/intel64/bin/pin.exe")
        pin_tool_path = os.path.abspath(f"./tools/pin-3.28-msvc-windows/tools/obj-intel64/{pintool}") # ilenmix
    else:
        raise Exception(architecture)
    
    with open(pin_stdout_path, 'w') as output_file, open(pin_stderr_path, 'w') as error_file:
        pin_proc = Popen(f"\"{pin_path}\" -logfile \"{pin_log_path}\" -error_file \"{pin_error_path}\" -t \"{pin_tool_path}\" -o \"{pintool_out_path}\" -- \"{file}\"", shell=True, stdout=output_file, stderr=error_file)
    
    wait_until_finish(pin_proc)
    instr_proc_task_kill(target_file_name)
    instr_proc_task_kill(target_file_name, True)
    wait_until_finish(pin_proc, timeout=5)
    proc_kill_force(pin_proc)

    pattern = r'Count\[(\d+)\]\s*=\s*(\d+)'

    with open(pintool_out_path, 'r') as file:
        text = file.read()

    matches = re.findall(pattern, text)
    pin_tool_success = False
    if len(matches):
        pin_tool_success = True

    try:
        returncode = pin_proc.returncode
    except:
        returncode = 2032 # Erro ao obter o returncode do instrumentador

    pin_dict = {
        "pin_returncode": returncode,
        "pin_tool_success": pin_tool_success
    }

    print("[Pin] Instrumentaçao concluida")

    with open(pin_run_data_path, 'w') as json_file:
        json.dump(pin_dict, json_file, sort_keys=False, indent=4)
