import os
from subprocess import Popen

def run_die(file, out):
    die_path = os.path.abspath("./tools/die_win64_portable_3.07/diec.exe")
    p1 = Popen(f"\"{die_path}\" -djruaei \"{file}\" > \"{out}\"", shell=True)
    p1.wait()