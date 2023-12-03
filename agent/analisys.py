import json
import os
from utils import calculate_sha256_hash, compress_folder, task_kill, count_analisys_target
from sample_data import SampleUploader
from tool_die import DieRunner
from tool_floss import FlossRunner
from tool_pefile import PEFileRunner
from tool_capa import CapaRunner
from tool_yara import YaraRunner
from tool_vivisect import VivisectRunner
from tool_procmon import ProcmonRunner
from tool_inst_pin import PinRunner
from tool_inst_dynamorio import DynamorioRunner
from tool_inst_frida import FridaRunner
import sys
from timer import Timer

def save_json(dict, path):
    with open(path, 'w') as json_file:
        json.dump(dict, json_file, indent = 4, sort_keys=True)

def process(result_server_ip="localhost", action=None):
    try:
        timer = Timer()
        timer.start()
        file_path = None 
        path_analisys = os.path.abspath("./in/")
        path_processed = os.path.abspath("./out/")
        path_compressed = os.path.abspath("./compressed/")

        if not os.path.exists(path_analisys):
            os.mkdir(path_analisys)

        if not os.path.exists(path_processed):
            os.mkdir(path_processed)

        if not os.path.exists(path_compressed):
            os.mkdir(path_compressed)
            
        sample_uploader = SampleUploader(base_url=f"http://{result_server_ip}:5000")
        samples = sample_uploader.get_sample_list()
        #print("Amostras processadas", len(samples))

        index = 0
        for current_folder, _, files in os.walk(path_analisys):
            for file in files:
                file_path = os.path.join(current_folder, file                                                                                                                                 )
                if not os.path.isfile(file_path):
                    continue

                if not os.access(file_path, os.X_OK):
                    continue

                index += 1
                hash = calculate_sha256_hash(file_path)
                out_dir = os.path.join(path_processed, hash)
                
                sample_isprocessed = list(filter(lambda x: x["hash_sha256"] == hash, samples)) and True or False
                if sample_isprocessed:
                    file_path = None
                    continue
                break

        if file_path == None:
            sample_uploader.disable_analisys()
            print("Análise concluída.")
            exit(0)

        print('Processando o arquivo ' + str(index) + ' de ' + str(count_analisys_target(path_analisys)))

        # Registrar o arquivo antes de analisar, se a análise falhar em algum ponto evitará que o arquivo seja analisado novamente 
        sample_uploader.register_sample(hash)
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        print("Analizando arquivo", file_name)

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        try:
            pefile_runner = PEFileRunner(file_path, out_dir)
            pefile_runner.run()
            architecture = pefile_runner.architecture
        except Exception as e:
            print(e)

        try:
            die_runner = DieRunner(file_path, out_dir)
            die_runner.run()
        except Exception as e:
            print(e)
            
        try:
            floss_runner = FlossRunner(file_path, out_dir)
            floss_runner.run()
        except Exception as e:
            print(e)
        
        try:
            capa_runner = CapaRunner(file_path, out_dir)
            capa_runner.run()
        except Exception as e:
            print(e)
                    
        try:
            yara_runner = YaraRunner(file_path, out_dir)
            yara_runner.run()
        except Exception as e:
            print(e)
            
        try:
            vivisect_runner = VivisectRunner(file_path, out_dir)
            vivisect_runner.run()
        except Exception as e:
            print(e)
            
        try:
            procmon_runner = ProcmonRunner(file_path, out_dir)
            procmon_runner.run()
        except Exception as e:
            print(e)

        try:
            pin_runner = PinRunner(file_path, out_dir, architecture)
            pin_runner.run()
        except Exception as e:
            print(e)

        try:
            dynamorio_runner = DynamorioRunner(file_path, out_dir, architecture)
            dynamorio_runner.run()
        except Exception as e:
            print(e)

        try:
            frida_runner = FridaRunner(file_path, out_dir)
            frida_runner.run()
        except Exception as e:
            print(e)

        target_file_name = os.path.basename(file_path)
        task_kill(target_file_name, True)

        zip_file = os.path.join(path_compressed,  f"{hash}.zip")
        compress_folder(out_dir, zip_file)
        
        sample_uploader.upload_sample_data_file(zip_file, hash)
        
    finally:
        try:
            timer.stop()
            
            file_info = {
                "file_name": file_name,
                "file_size": file_size,
                "hash": hash,
                "out_dir": out_dir,
                "in_dir": file_path,
                "execution_time": str(timer.formatted_time()),
                "execution_timedelta": str(timer.as_timedelta())
            }

            try:
                save_out = os.path.join(out_dir, "file_info.json")
                save_json(file_info, save_out)
            except Exception as e:
                print(e)
            sample_uploader.register_sample(hash)
        except:
            pass
        if os.name == 'nt':   # Para Windows
            if action == 'restart':
                os.system("shutdown /r /t 0")
            elif action == 'shutdown':
                os.system("shutdown /s /t 0")
            elif action == 'exit-script':
                exit(0)
            else:
                print("Ação não enviada.")

def main():
    if len(sys.argv) < 3:
        print("Uso: python script.py <ip_do_serviço> <acao_post_execucao>")
        print("Onde <acao_post_execucao> pode ser 'restart', 'shutdown' ou 'exit-script'.")
        return

    result_server_ip = sys.argv[1]
    action = sys.argv[2]
    process(result_server_ip, action)

if __name__ == "__main__":
    main()
