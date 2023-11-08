import os
import subprocess
from pathlib import Path
import sys
from tool_runner_base import ToolRunner
from utils import ensure_directory_exists, log_error_file

class CapaRunner(ToolRunner):
    def __init__(self, file_path, out):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "capa")
        self.out_dir = ensure_directory_exists(out_dir)

    @staticmethod
    @log_error_file
    def __run(file_path, out_dir):
        print("Executando CAPA...")
        out_path = os.path.join(out_dir, "capa.json")
        capa_path = os.path.abspath("./tools/capa/capa.exe")
        rules_path = os.path.abspath("./tools/capa/capa-rules")
        subprocess.run(f'"{capa_path}" -q -r "{rules_path}" -j "{file_path}" > "{out_path}" 2>&1', shell=True)
        return out_path

    def run(self):
        return CapaRunner.__run(self.file_path, self.out_dir)


def main():
    if len(sys.argv) < 3:
        print("Uso: python tool_capa.py <arquivo> <saída>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]

    capa_runner = CapaRunner(file, out)
    result_path = capa_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()