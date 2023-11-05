import os
import subprocess
from pathlib import Path

def run_floss(file_path, out):
    print("Executando Floss")

    out_dir = os.path.join(out, "floss")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    out_path = os.path.join(out_dir, "floss.json")

    floss_path = os.path.abspath("./tools/floss/floss.exe") 
    res_path = Path(out_path)
    p = subprocess.run(f'{floss_path} --only static -j "{file_path}"', shell=True, check=True, capture_output=True)
    with res_path.open("w") as f:
        f.write(p.stdout.decode("utf-8"))
    return str(res_path)
