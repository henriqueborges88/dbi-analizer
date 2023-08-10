import hashlib
from subprocess import Popen, getoutput
import zipfile
import os
from time import sleep

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


def wait_until_finish(proccess, timeout=10):
    '''
    Espera até o processo finalizar a execução ou até alcançar o tempo máximo de espera
        Parámetros:
            proccess: Processo do instrumentador
            timeout: Tempo máxiomo de espera para a finalização do executável   
    '''
    wait_secconds = 0
    while proccess.poll() is None and wait_secconds < timeout:
        wait_secconds +=1
        sleep(1)

def instr_proc_task_kill(proccess, file_name, timeout=10):
    '''
    Envia o sinal de finalização para o executável que está sendo instrumentado
        Parámetros:
            proccess: Processo do instrumentador
            file_name: Nome do arquivo executável sendo intrumentado
            timeout: Tempo máxiomo de espera para a finalização do executável
    '''
    p_tasklist_wait_secconds = 0
    p_tasklist  = (getoutput( f"tasklist | findstr \"{file_name}\"")).strip()
    while proccess.poll() is None and file_name in p_tasklist and p_tasklist_wait_secconds < timeout:
        p_tasklist_wait_secconds += 1
        p_kill = Popen(f"taskkill /IM {file_name} > NUL 2> NUL", shell=True)
        p_kill.wait()
        sleep(1)
        p_tasklist  = (getoutput( f"tasklist | findstr \"{file_name}\"")).strip()

def instr_proc_task_kill_force(proccess, file_name):
    '''
    Envia o sinal de finalização forçada para o executável que está sendo instrumentado
        Parámetros:
            proccess: Processo do instrumentador
            file_name: Nome do arquivo executável sendo intrumentado
    '''
    if proccess.poll() is None:
        p_kill = Popen(f"taskkill /F /IM {file_name} > NUL 2> NUL", shell=True)
        p_kill.wait()
        p_kill.terminate()
        p_kill.kill()

def proc_kill_force(proccess):
    if proccess.poll() is None:
        proccess.terminate()
    sleep(2)
    if proccess.poll() is None: 
        proccess.kill()