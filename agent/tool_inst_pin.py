import json
import os
import re
from subprocess import Popen
import sys
from utils import wait_until_finish, instr_proc_task_kill, proc_kill_force
from timer import Timer
from pathlib import Path
from tool_runner_base import ToolRunner
from utils import ensure_directory_exists, log_error_file

class PinRunner(ToolRunner):
    def __init__(self, file_path, out, architecture):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "pin")
        self.out_dir = ensure_directory_exists(out_dir)
        self.architecture = architecture

    @staticmethod
    @log_error_file
    def __run(file_path, out_dir, architecture):
        print("Executando Pin...")
        timer = Timer()
        timer.start()
        
        pin_run_data_path = os.path.join(out_dir, "pin_run_data.txt")
        pin_log_path = os.path.join(out_dir, "pin_log.txt")
        pin_error_path = os.path.join(out_dir, "pin_error.txt")
        pintool_out_path = os.path.join(out_dir, "pintool_out.txt")
        pin_stderr_path = os.path.join(out_dir, 'pin_stderr.txt')
        pin_stdout_path = os.path.join(out_dir, 'pin_stdout.txt')
        target_file_name = os.path.basename(file_path)
        pintool = "calltrace.dll" #"inscount2_mt.dll"
        
        if architecture == "32 bits":
            pin_path = os.path.abspath("./tools/pin-3.28-msvc-windows/ia32/bin/pin.exe")
            pin_tool_path = os.path.abspath(f"./tools/pin-3.28-msvc-windows/tools/obj-ia32/{pintool}") # ilenmix
        elif architecture == "64 bits":
            pin_path = os.path.abspath("./tools/pin-3.28-msvc-windows/intel64/bin/pin.exe")
            pin_tool_path = os.path.abspath(f"./tools/pin-3.28-msvc-windows/tools/obj-intel64/{pintool}") # ilenmix
        else:
            raise Exception(architecture)
        
        with open(pin_stdout_path, 'w') as output_file, open(pin_stderr_path, 'w') as error_file:
            pin_proc = Popen(f"\"{pin_path}\" -logfile \"{pin_log_path}\" -error_file \"{pin_error_path}\" -t \"{pin_tool_path}\" -o \"{pintool_out_path}\" -- \"{file_path}\"", shell=True, stdout=output_file, stderr=error_file)
            
            wait_until_finish(pin_proc, timeout=10)
            instr_proc_task_kill(target_file_name)
            instr_proc_task_kill(target_file_name, True)
            wait_until_finish(pin_proc, timeout=5)
            proc_kill_force(pin_proc)

        line_count = 0
        with open(pintool_out_path, 'r') as file:
            for line in file:
                line_count += 1
        pin_tool_success = False
        if line_count > 0:
            pin_tool_success = True

        timer.stop()

        try:
            returncode = pin_proc.returncode
        except:
            returncode = 2032 # Erro ao obter o returncode do instrumentador

        pin_dict = {
            "pin_returncode": returncode,
            "pin_tool_success": pin_tool_success,
            "execution_time": str(timer.formatted_time()),
            "execution_timedelta": str(timer.as_timedelta())
        }

        print("[Pin] Instrumentação concluída")

        with open(pin_run_data_path, 'w') as json_file:
            json.dump(pin_dict, json_file, sort_keys=False, indent=4)

        return pin_run_data_path

    def run(self):
        return PinRunner.__run(self.file_path, self.out_dir, self.architecture)


def main():
    if len(sys.argv) < 4:
        print("Uso: python tool_inst_pin.py <arquivo> <saída> <arquitetura -> {'32 bits','64 bits'}>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]
    architecture = sys.argv[3]

    pin_runner = PinRunner(file, out, architecture)
    result_path = pin_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()