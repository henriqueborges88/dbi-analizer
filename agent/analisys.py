import json
import os
# from run_inst_pyqbdi import run_pyqbdi
from run_inst_dynamorio import run_dynamorio
from utils import calculate_sha256_hash, compress_folder
from sample_data import SampleUploader
from run_die import run_die
from run_floss import run_floss
from run_pe import run_pe
from run_vivisect import run_vivisect
from run_inst_pin import run_pin
from run_inst_frida import run_frida
import sys

def save_json(dict, path):
    with open(path, 'w') as json_file:
        json.dump(dict, json_file, indent = 4, sort_keys=True)

def process(result_server_ip="localhost"):
        
    path_analisys = os.path.abspath("./in/")
    path_processed = os.path.abspath("./out/")

    sample_uploader = SampleUploader(base_url=f"http://{result_server_ip}:5000")
    samples = sample_uploader.get_sample_list()
    print("Amostras processadas", len(samples))

    list_dir = os.listdir(path_analisys)
    for index, filename in enumerate(list_dir):
        file = os.path.join(path_analisys, filename)
        if not os.path.isfile(file):
            continue
        file_name = os.path.basename(file)
        hash = calculate_sha256_hash(file)

        sample_uploader.register_sample(hash)
        
        out_dir = os.path.join(path_processed, hash)
        
        file_info = {
            "file_name": file_name,
            "hash": hash,
            "out_dir": out_dir,
            "in_dir": file
        }

        sample_isprocessed = list(filter(lambda x: x["sample_hash_sha256"] == hash, samples)) and True or False
        if sample_isprocessed:
            continue

        print("Analizando arquivo", file_name)

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        try:
            save_out = os.path.join(out_dir, "info_out.json")
            save_json(file_info, save_out)
        except Exception as e:
            print(e)

        try:
            pe_out = os.path.join(out_dir, "pe_out.json")
            architecture = run_pe(file, pe_out, True)
        except Exception as e:
            print(e)

        # try:
        #     die_out = os.path.join(out_dir, "die_out.json")
        #     run_die(file, die_out)
        # except Exception as e:
        #     print(e)
            
        # try:
        #     floss_out = os.path.join(out_dir, "strings_out.json")
        #     run_floss(file, floss_out)
        # except Exception as e:
        #     print(e)
        
        # try:
        #     run_vivisect(file, out_dir)
        # except Exception as e:
        #     print(e)
            
        try:
            
            run_pin(file, architecture, out_dir)
        except Exception as e:
            print(e)
        
        # try:
        #     pin_out = os.path.join(out_dir, "frida_out.txt")
        #     run_frida(file, pin_out)
        # except Exception as e:
        #     print(e)

        # try:
        #     dynamorio_out = os.path.join(out_dir, "dynamorio_out.txt")
        #     run_dynamorio(file, architecture, dynamorio_out)
        # except Exception as e:
        #     print(e)
    
            
        # try:
        #     pyqbdi_out = os.path.join(out_dir, "pyqbdi_out.json")
        #     run_pyqbdi(file, pyqbdi_out)
        # except Exception as e:
        #     print(e)
        
        zip_file = f"compressed/{hash}.zip"
        compress_folder(out_dir, zip_file)
        
        sample_uploader.upload_sample_data_file(zip_file, hash)

        print('Processado ' + str(index + 1) + ' de ' + str(len(list_dir)))

def main():
    if len(sys.argv) < 1:
        print("Uso: python script.py ip do serviço que registrará os resultados...")
        return

    result_server_ip = sys.argv[1]
    process(result_server_ip)

if __name__ == "__main__":
    main()
