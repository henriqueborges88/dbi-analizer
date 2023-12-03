import shutil
import os
import zipfile
import socket

def compress_folder(source_folder, zip_file):
    shutil.make_archive(os.path.splitext(zip_file)[0], 'zip', source_folder)

def decompress_zip(zip_file, target_folder):
    """
    Decompress a zip file into a specific target directory.

    :param zip_file: Path of the zip file to be decompressed.
    :param target_folder: Target directory where the contents of the zip will be extracted.
    """
    
    # Create target directory if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Open the zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # Extract all the contents into the target directory
        zip_ref.extractall(target_folder)

def decompress_specific_file(zip_file, target_folder, file_name):
    """
    Decompress a specific file from a zip archive into a target directory.

    :param zip_file: Path of the zip file.
    :param target_folder: Target directory where the file will be extracted.
    :param file_name: Name of the specific file to be extracted from the zip.
    """
    # Create target directory if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Open the zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # Check if the specified file exists in the zip
        if file_name in zip_ref.namelist():
            # Extract the specific file into the target directory
            zip_ref.extract(file_name, target_folder)
            return True
        else:
            print(f"File {file_name} not found in the zip archive {zip_file}.")
            return False

def decompress_specific_folder(zip_file, target_folder, folder_name):
    """
    Decompress a specific folder from a zip archive into a target directory.

    :param zip_file: Path of the zip file.
    :param target_folder: Target directory where the folder will be extracted.
    :param folder_name: Name of the specific folder to be extracted from the zip.
    """
    # Create target directory if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Open the zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # Extract only the files from the specified folder
        for file in zip_ref.namelist():
            if file.startswith(folder_name):
                zip_ref.extract(file, target_folder)


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

def ensure_directory_exists(out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    return out_dir