from functools import wraps
import hashlib
from subprocess import Popen, getoutput
import subprocess
import zipfile
import os
from time import sleep
from datetime import date, datetime
import json

class DictEncoder(json.JSONEncoder):
    def key_to_json(self, data):
        if data is None or isinstance(data, (bool, int, str)):
            return data
        if isinstance(data, (bytearray, bytes)):
            return data.decode('UTF-8')
        if isinstance(data, (tuple, frozenset)):
            return str(data)
        return "Undefined"

    def default(self, obj):
        if isinstance(obj, (bytearray, bytes)):
            return obj.decode('UTF-8')
        if isinstance(obj, (date, datetime)):
            return obj.timestamp()
        if obj is None or isinstance(obj, (bool, int, tuple, range, str, list)):
            return obj
        if isinstance(obj, (set, frozenset)):
            return sorted(obj)
        if isinstance(obj, dict):
            return {self.key_to_json(key): self.default(obj[key]) for key in obj}
        if isinstance(obj, (list, tuple)):
            return [self.default(item) for item in obj]
        try:
            return super().default(obj)
        except TypeError as e:
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable: {e}")


def calculate_sha256_hash(file_path):
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(block)

    # Return the hexadecimal representation of the SHA-256 hash
    return sha256_hash.hexdigest()


def compress_folder(source_folder, zip_file):
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for current_folder, _, files in os.walk(source_folder):
            for file in files:
                full_path = os.path.join(current_folder, file)

                relative_path = os.path.relpath(full_path, source_folder)

                zipf.write(full_path, relative_path)

def count_analisys_target(path_analisys):
    count = 0
    for current_folder, _, files in os.walk(path_analisys):
        for file in files:
            file_path = os.path.join(current_folder, file)
            if not os.path.isfile(file_path):
                continue

            if not os.access(file_path, os.X_OK):
                continue
            count += 1
    return count

def wait_until_finish(proccess, timeout=40):
    '''
    Espera até o processo finalizar a execução ou até alcançar o tempo máximo de espera
        Parámetros:
            proccess: Processo
            timeout: Tempo máxiomo de espera para a finalização do executável   
    '''
    wait_secconds = 0
    while proccess.poll() is None and wait_secconds < timeout:
        wait_secconds +=1
        sleep(1)

def task_kill(file_name, force=False, timeout=10):
    '''
    Envia o sinal de finalização para o executável que está sendo instrumentado
        Parámetros:
            proccess: Processo
            file_name: Nome do arquivo executável sendo intrumentado
            timeout: Tempo máxiomo de espera para a finalização do executável
    '''
    force_param = ""
    if force:
        force_param = "/F"
    p_tasklist_wait_secconds = 0
    p_kill = Popen(f"taskkill {force_param} /IM {file_name} > NUL 2> NUL", shell=True)
    p_kill.wait()
    p_tasklist  = (getoutput( f"tasklist | findstr \"{file_name}\"")).strip()
    while file_name in p_tasklist and p_tasklist_wait_secconds < timeout:
        p_tasklist_wait_secconds += 1
        p_kill = Popen(f"taskkill {force_param} /IM {file_name} > NUL 2> NUL", shell=True)
        p_kill.wait()
        sleep(1)
        p_tasklist  = (getoutput( f"tasklist | findstr \"{file_name}\"")).strip()

def proc_kill_force(proccess):
    if proccess.poll() is None:
        proccess.terminate()
    sleep(2)
    if proccess.poll() is None: 
        proccess.kill()


def ensure_directory_exists(out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    return out_dir

def log_error_file(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) < 2:
            raise ValueError("file_path e out_dir são obrigatórios")
        file_path, out_dir = args[:2]
        error_path = os.path.join(out_dir, "errors.log")
        try:
            return func(*args, **kwargs)  # Passa todos os argumentos recebidos
        except subprocess.CalledProcessError as ex:
            with open(error_path, "w") as f:
                f.write(str(ex.stderr))
            return None
        except Exception as ex:
            with open(error_path, "w") as f:
                f.write(str(ex))
            return None
    return wrapper