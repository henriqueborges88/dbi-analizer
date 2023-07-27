import subprocess
from pathlib import Path

def run_floss(file_path, out_json):
    res_path = Path(out_json)
    p = subprocess.run(f'python -m floss -j "{file_path}"', shell=True, check=True, capture_output=True)
    with res_path.open("w") as f:
        f.write(p.stdout.decode("utf-8"))
    return str(res_path)
