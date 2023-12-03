import json
import os
from subprocess import Popen
import sys
from time import sleep
from utils import wait_until_finish, task_kill, proc_kill_force
from timer import Timer
from pathlib import Path
from tool_runner_base import ToolRunner
from utils import ensure_directory_exists, log_error_file

class DynamorioRunner(ToolRunner):
    def __init__(self, file_path, out, architecture):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "dynamorio")
        self.out_dir = ensure_directory_exists(out_dir)
        self.architecture = architecture

    @staticmethod
    @log_error_file
    def __run(file_path, out_dir, architecture):
        print("Executando Dynamorio...")
        timer = Timer()
        timer.start()

        dynamorio_run_data_path = os.path.join(out_dir, "dynamorio_run_data.json")
        dynamorio_tool_out_path = os.path.join(out_dir, 'dynamorio_tool_out.txt')
        if architecture == "32 bits":
            dynamorio_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin32/drrun.exe")
            drkill_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin32/DRkill.exe")
        elif architecture == "64 bits":
            dynamorio_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin64/drrun.exe")
            drkill_path = os.path.abspath("./tools/DynamoRIO-Windows-9.0.1/bin64/DRkill.exe")
        else:
            raise Exception(architecture)
        
        target_file_name = os.path.basename(file_path)
        
        dynamorio_proc = Popen(f"\"{dynamorio_path}\" -s 40 -exit0 -no_inject -t drcachesim -simulator_type basic_counts -- \"{file_path}\" > {dynamorio_tool_out_path} 2>&1", shell=True)

        wait_until_finish(dynamorio_proc, timeout=15)
        task_kill(target_file_name)
        task_kill(target_file_name, True)
        wait_until_finish(dynamorio_proc, timeout=5)
        proc_kill_force(dynamorio_proc)
        Popen(f"\"{drkill_path}\" -underdr", shell=True)
        sleep(2)
                
        with open(dynamorio_tool_out_path, 'r') as file:
            text = file.read()
            
        dynamorio_tool_success = False

        if "Basic counts tool results:" in text:
            dynamorio_tool_success = True

        try:
            returncode = dynamorio_proc.returncode
        except:
            returncode = 2032 # Erro ao obter o returncode do instrumentador

        timer.stop()

        dynamorio_dict = {
            "dynamorio_returncode": returncode,
            "dynamorio_tool_success": dynamorio_tool_success,
            "execution_time": str(timer.formatted_time()),
            "execution_timedelta": str(timer.as_timedelta())
        }

        print("[Dynamorio] Instrumentação concluída")

        with open(dynamorio_run_data_path, 'w') as json_file:
            json.dump(dynamorio_dict, json_file, sort_keys=False, indent=4)

        return dynamorio_run_data_path

    def run(self):
        return DynamorioRunner.__run(self.file_path, self.out_dir, self.architecture)


def main():
    if len(sys.argv) < 4:
        print("Uso: python tool_inst_dynamorio.py <arquivo> <saída> <arquitetura -> {'32 bits','64 bits'}>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]
    architecture = sys.argv[3]

    dynamorio_runner = DynamorioRunner(file, out, architecture)
    result_path = dynamorio_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()