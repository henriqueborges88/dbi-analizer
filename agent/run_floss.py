import os
import subprocess
from pathlib import Path

def run_floss(file_path, out_json):
    floss_path = os.path.abspath("./tools/floss.exe") 
    res_path = Path(out_json)
    p = subprocess.run(f'{floss_path} -j "{file_path}"', shell=True, check=True, capture_output=True)
    with res_path.open("w") as f:
        f.write(p.stdout.decode("utf-8"))
    return str(res_path)
