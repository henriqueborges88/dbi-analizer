import sys
import pefile
import json
import hashlib
import os
from pathlib import Path
from tool_runner_base import ToolRunner
from utils import DictEncoder, ensure_directory_exists, log_error_file


BLOCKSIZE = 65536

def convert_bytes_and_skip_noniterables(obj):
    """
    Converte bytes e bytearrays em strings de um objeto de forma recursiva
    e desconsidera objetos NoneType e não iteráveis.

    :param obj: Objeto (pode ser dicionário ou lista) para processar.
    :return: Objeto com bytes e bytearrays convertidos, None e não iteráveis desconsiderados.
    """
    if not isinstance(obj, (dict, list)):
        raise ValueError("O objeto fornecido não é um dicionário nem uma lista")

    def is_iterable(value):
        return isinstance(value, (list, dict))

    def convert_bytes(value):
        if isinstance(value, (bytes, bytearray)):
            try:
                return value.decode('UTF-8')
            except UnicodeDecodeError:
                return None
        return value

    if isinstance(obj, list):
        # Se for uma lista, processa cada item recursivamente.
        return [convert_bytes_and_skip_noniterables(item) for item in obj
                if item is not None and is_iterable(item)]
    
    elif isinstance(obj, dict):
        converted_dict = {}
        for key, value in obj.items():
            if value is None:
                # Se o valor for None, pula a chave.
                continue
            # Converte chaves se forem do tipo bytes ou bytearray.
            converted_key = convert_bytes(key)
            if is_iterable(value):
                # Se o valor for iterável, processa-o recursivamente.
                converted_dict[converted_key] = convert_bytes_and_skip_noniterables(value)
            else:
                # Se o valor for um tipo de dados primitivo, tenta convertê-lo se for bytes.
                converted_value = convert_bytes(value)
                if converted_value is not None:
                    converted_dict[converted_key] = converted_value
        return converted_dict


class PEFileRunner(ToolRunner):
    def __init__(self, file_path, out):
        super().__init__(file_path, out)
        out_dir = os.path.join(out, "pefile")
        self.out_dir = ensure_directory_exists(out_dir)
        self.architecture = None
        
    @staticmethod
    @log_error_file
    def __run(file, out_dir):
        print("Executando PEFile...")  
        out_path = os.path.join(out_dir, "pefile.json")

        pe = pefile.PE(file)
        pe.parse_data_directories( directories=[         
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_BASERELOC'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DEBUG'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_COPYRIGHT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_GLOBALPTR'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_TLS'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IAT']
            ] )

        pe_dict = dict()
        
        pe_dict['name'] = os.path.basename(file)

        pe_dict['size'] = os.path.getsize(file)

        # md5, sha-1, sha-256, sha-512
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()
        with open(file, 'rb') as file:
            buffer = file.read(BLOCKSIZE)
            while len(buffer) > 0:
                md5.update(buffer)
                sha1.update(buffer)
                sha256.update(buffer)
                sha512.update(buffer)
                buffer = file.read(BLOCKSIZE)
        pe_dict['md5'] = md5.hexdigest()
        pe_dict['sha-1'] = sha1.hexdigest()
        pe_dict['sha-256'] = sha256.hexdigest()
        pe_dict['sha-512'] = sha512.hexdigest()

        pe_dict['imphash'] = pe.get_imphash()

        pe_dict.update(pe.dump_dict())
        if "Version Information" in pe_dict:
            pe_dict["Version Information"] = convert_bytes_and_skip_noniterables(pe_dict["Version Information"])
    
        with open(out_path, 'w') as json_file:
            json.dump(pe_dict, json_file, cls=DictEncoder, sort_keys=False, indent=4)

        pe.close()

        architecture = next(iter(list(filter(lambda machine_type: pefile.MACHINE_TYPE[machine_type] == pe.FILE_HEADER.Machine, pefile.MACHINE_TYPE))), None)
        if architecture == 'IMAGE_FILE_MACHINE_I386':
            architecture = '32 bits'
        elif architecture == 'IMAGE_FILE_MACHINE_AMD64':
            architecture = '64 bits'
    
        return out_path, architecture
    
    def run(self):
        run_out, architecture = PEFileRunner.__run(self.file_path, self.out_dir)
        self.architecture = architecture
        return run_out


def main():
    if len(sys.argv) < 3:
        print("Uso: python tool_pefile.py <arquivo> <saída>")
        return 
    file = sys.argv[1]
    out = sys.argv[2]

    pefile_runner = PEFileRunner(file, out)
    result_path = pefile_runner.run()
    print(f"O resultado foi salvo no arquivo -> {result_path}")

if __name__ == "__main__":
    main()