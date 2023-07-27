import json
import os
import re
from subprocess import Popen, getoutput, PIPE, STDOUT
from time import sleep

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

    p_tasklist_wait_secconds = 0
    p_tasklist  = (getoutput( f"tasklist | findstr \"{file_name}\"")).strip()
    while pin_proc.poll() is None and file_name in p_tasklist and p_tasklist_wait_secconds < 30:
        p_tasklist_wait_secconds += 1
        p_kill = Popen(f"taskkill /IM {file_name} > NUL 2> NUL", shell=True)
        p_kill.wait()
        sleep(1)
        p_tasklist  = (getoutput( f"tasklist | findstr \"{file_name}\"")).strip()

    if pin_proc.poll() is None:
        p_kill = Popen(f"taskkill /F /IM {file_name} > NUL 2> NUL", shell=True)
        p_kill.wait()
        p_kill.terminate()
        p_kill.kill()

    try:
        pin_out, pin_error = pin_proc.communicate()
        pin_out = pin_out.decode(errors='replace')
        pin_error = pin_error.decode(errors='replace')

        i_count = 0
        p_count = r'Count (\d+)$'
        match = re.search(p_count, pin_out)
        if match:
            i_count = match.group(1)
        
        pin_dict = {
            "output": pin_out,
            "has_error": pin_error and False or True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
            "intructions_count": i_count
        }
    except Exception as ex:
        pin_dict = {
            "output": "Tempo limite esgotado",
            "has_error": True, # O instruction count envia a contagem para a saiída stderror, por tanto se a saída está vazía, a contagem falhou.
            "intructions_count": 0
        }

    with open(out, 'w') as json_file:
        json.dump(pin_dict, json_file, sort_keys=False, indent=4)
