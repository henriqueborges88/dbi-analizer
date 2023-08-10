import pefile
import json
from datetime import date, datetime
import hashlib
import os

BLOCKSIZE = 65536

class pe_encoder(json.JSONEncoder):
    def key_to_json(self, data):
        if data is None or isinstance(data, (bool, int, str)):
            return data
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
        try:
            return json.JSONEncoder.default(self, obj)
        except:
            return None


def run_pe(filepath, out, pretty):
    pe = pefile.PE(filepath)
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
    
    # name
    pe_dict['name'] = os.path.basename(filepath)

    # size
    pe_dict['size'] = os.path.getsize(filepath)

	# md5, sha-1, sha-256, sha-512
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()
    with open(filepath, 'rb') as file:
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

	# imphash
    pe_dict['imphash'] = pe.get_imphash()

	# Add the whole pe to the dictionnary
    pe_dict.update({"DOS_HEADER": pe.dump_dict()["DOS_HEADER"]})
    pe_dict.update({"NT_HEADERS": pe.dump_dict()["NT_HEADERS"]})
    pe_dict.update({"FILE_HEADER": pe.dump_dict()["FILE_HEADER"]})
    pe_dict.update({"Flags": pe.dump_dict()["Flags"]})
    pe_dict.update({"OPTIONAL_HEADER": pe.dump_dict()["OPTIONAL_HEADER"]})
    pe_dict.update({"DllCharacteristics": pe.dump_dict()["DllCharacteristics"]})
    pe_dict.update({"PE_Sections": pe.dump_dict()["PE Sections"]})
    pe_dict.update({"Directories": pe.dump_dict()["Directories"]})
    #pe_dict.update({"Version_Information": pe.dump_dict()["Version Information"]})
    pe_dict.update({"Imported_symbols": pe.dump_dict()["Imported symbols"]})
    pe_dict.update({"Resource_directory": pe.dump_dict()["Resource directory"]})
 
    # Make a json file
    if (pretty is True):
        with open(out, 'w') as json_file:
            json.dump(pe_dict, json_file, cls=pe_encoder, sort_keys=False, indent=4)
    else:
        with open(out, 'w') as json_file:
            json.dump(pe_dict, json_file, cls=pe_encoder, sort_keys=False)

    pe.close()

    if pe.FILE_HEADER.Machine == pefile.MACHINE_TYPE['IMAGE_FILE_MACHINE_I386']:
        return '32 bits'
    elif pe.FILE_HEADER.Machine == pefile.MACHINE_TYPE['IMAGE_FILE_MACHINE_AMD64']:
        return '64 bits'
    else:
        return 'Arquitetura desconhecida'
 