import yara
import os
import json
import subprocess
from pathlib import Path
import sys
from tool_runner_base import ToolRunner
from utils import DictEncoder, ensure_directory_exists, log_error_file

class YaraRunner(ToolRunner):
    def __init__(self, file_path, out):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "yara")
        self.out_dir = ensure_directory_exists(out_dir)
        self.rules_dir = os.path.abspath("./tools/yara/yara-rules")
        self.compiled_rules = ""
        self.compile_yara_rules()

    def compile_yara_rules(self):
        antidebug_antivm_path = os.path.join(self.rules_dir, "antidebug_antivm_index.yar")
        packers_path = os.path.join(self.rules_dir, "packers_index.yar")
        print("[YAYA] Compilando regras...")
        rules = yara.compile(filepaths={
            'antidebug_antivm': antidebug_antivm_path,
            'packers': packers_path
        })
        self.compiled_rules = rules
            
    @staticmethod
    @log_error_file
    def __run(file_path, out_dir, compiled_rules):
        print("Executando YARA...")
        out_path = os.path.join(out_dir, "yara.json")
        print("[YAYA] Analisando arquivo...")
        matches = compiled_rules.match(file_path)
        ms = []
        for match in matches:
            m = match.meta
            m.update({"tags": match.tags})
            m.update({"namespace": match.namespace})
            m.update({"rule": match.rule})
            ms.append(m)
        result = {
            "matches": ms
        }
        with open(out_path, 'w') as json_file:
            json.dump(result, json_file, cls=DictEncoder, sort_keys=False, indent=4)

        return out_path

    def run(self):
        return YaraRunner.__run(self.file_path, self.out_dir, self.compiled_rules)


def main():
    if len(sys.argv) < 3:
        print("Uso: python tool_yara.py <arquivo> <saída>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]

    capa_runner = YaraRunner(file, out)
    result_path = capa_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()