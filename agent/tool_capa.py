import os
import subprocess
from pathlib import Path

def run_capa(file_path, out):
    print("Executando capa")

    out_dir = os.path.join(out, "capa")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    out_json_path = os.path.join(out_dir, "capa.json")
    capa_path = os.path.abspath("./tools/capa/capa.exe")
    rules_path = os.path.abspath("./tools/capa/capa-rules") 
    subprocess.run(f'{capa_path} -r {rules_path} -j "{file_path}" > {out_json_path}')

    res_path = Path(out_json_path)
    return str(res_path)
