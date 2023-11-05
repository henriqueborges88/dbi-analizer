import os
from subprocess import Popen

def run_die(file, out):
    print("Executando DIE")
    
    out_dir = os.path.join(out, "die")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    out_path = os.path.join(out_dir, "die.json")
    die_path = os.path.abspath("./tools/die_win64_portable_3.07/diec.exe")
    p1 = Popen(f"\"{die_path}\" -djruaei \"{file}\" > \"{out_path}\"", shell=True)
    p1.wait()