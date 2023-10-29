import shutil
import os
import zipfile
import socket

def compress_folder(source_folder, zip_file):
    shutil.make_archive(os.path.splitext(zip_file)[0], 'zip', source_folder)

def write_ip_to_file(option):
    with open("../agent/server_ip.txt", "w") as file:
        file.write(option)

def delete_all_files_and_folders(directory_path):
    try:
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print("Todos os arquivos e pastas foram removidos com sucesso.")
        return True
    except Exception as e:
        print(f"Ocorreu um erro ao tentar remover os arquivos e pastas: {e}")
        return False
