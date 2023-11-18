import os
import subprocess
from pathlib import Path
import sys
from tool_runner_base import ToolRunner
from utils import ensure_directory_exists, log_error_file
from utils import wait_until_finish, task_kill, proc_kill_force
from time import sleep
import shutil

class ProcmonRunner(ToolRunner):
    def __init__(self, file_path, out):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "procmon")
        self.out_dir = ensure_directory_exists(out_dir)

    @staticmethod
    @log_error_file
    def __run(file_path, out_dir):
        print("Executando Procmon...")
        file_tmp_dir = os.path.join(os.path.abspath("./"), "tmp")
        ensure_directory_exists(file_tmp_dir)
        file_name = "MaLwArEpRoCeSs.exe" # filter on procmon is configured to capture this name
        file_tmp_path = os.path.join(file_tmp_dir, file_name)
        shutil.copy2(file_path, file_tmp_path) 
        procmon_path = os.path.abspath("./tools/procmon/Procmon64.exe")
        config_path = os.path.abspath("./tools/procmon/ProcmonConfiguration.pmc")
        out_path = os.path.join(out_dir, "procmon.pml")
        out_filtered_path = os.path.join(out_dir, "procmon.xml")
        subprocess.Popen(f'"{procmon_path}" /AcceptEula /Quiet /Minimized /LoadConfig "{config_path}" /BackingFile "{out_path}"', shell=True)
        subprocess.run(f'"{procmon_path}" /AcceptEula /WaitForIdle', shell=True)
        sample_proc = subprocess.Popen(f"{file_tmp_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wait_until_finish(sample_proc, timeout=5)
        sample_proc.terminate()
        sleep(1)
        task_kill(file_name)
        task_kill(file_name, True)
        proc_kill_force(sample_proc)
        subprocess.run(f'"{procmon_path}" /AcceptEula /Quiet /Terminate', shell=True)
        subprocess.run(f'"{procmon_path}" /AcceptEula /Quiet /Minimized /LoadConfig "{config_path}" /OpenLog "{out_path}" /SaveAs2 "{out_filtered_path}" /SaveApplyFilter', shell=True)
        os.remove(file_tmp_path)
        return out_path

    def run(self):
        return ProcmonRunner.__run(self.file_path, self.out_dir)


def main():
    if len(sys.argv) < 3:
        print("Uso: python tool_procmon.py <arquivo> <saída>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]

    procmon_runner = ProcmonRunner(file, out)
    result_path = procmon_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()