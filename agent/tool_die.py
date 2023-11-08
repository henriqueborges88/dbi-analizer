import os
from pathlib import Path
import subprocess
import sys
from tool_runner_base import ToolRunner
from utils import ensure_directory_exists, log_error_file

class DieRunner(ToolRunner):
    def __init__(self, file_path, out):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "die")
        self.out_dir = ensure_directory_exists(out_dir)
    
    @staticmethod
    @log_error_file
    def __run(file, out_dir):
        print("Executando DIE...")   
        out_path = os.path.join(out_dir, "die.json")
        die_path = os.path.abspath("./tools/die_win64_portable_3.07/diec.exe")
        subprocess.run(f'"{die_path}" -djruaei "{file}" > "{out_path}" 2>&1', shell=True)
        return out_path
    
    def run(self):
        return DieRunner.__run(self.file_path, self.out_dir)


def main():
    if len(sys.argv) < 3:
        print("Uso: python tool_die.py <arquivo> <saída>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]

    die_runner = DieRunner(file, out)
    result_path = die_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()