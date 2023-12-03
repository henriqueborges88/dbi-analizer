import sys
import os
from models import db, CapaInfo, YaraInfo, DieInfo, Sample
from controllers.sample_controller import insert_sample, update_pin_tool_success, update_dynamorio_tool_success, update_frida_tool_success, update_sample_status
from utils import decompress_specific_file, ensure_directory_exists
from process_capa import process_capa
from process_yara import process_yara
from process_die import process_die


def process_result(file_path):
    file_name = os.path.basename(file_path)
    file_name_without_extension, _ = os.path.splitext(file_name)
    sample_hash256_or_id = file_name_without_extension.replace(" ", "_")
    out_dir = ensure_directory_exists(f"tmp/{sample_hash256_or_id}")
    
    sample = Sample.query.get(sample_hash256_or_id)
    if not sample:
        if not insert_sample(sample_hash256_or_id):
            raise Exception(f"Não foi possével regustrar a amostra {sample_hash}")
    
    # PIN
    try:
        pin_success = False
        pin_path_zip = "pin/pin_run_data.json"
        decompress_pin = decompress_specific_file(file_path, out_dir, pin_path_zip)
        if decompress_pin:
            pin_out_path = os.path.join(out_dir, pin_path_zip)
            with open(pin_out_path, 'r') as file_pin:
                data_pin = json.load(file_pin)
                pin_success = bool(data_pin["pin_tool_success"])
                update_pin_tool_success(sample_hash256_or_id, pin_success)
    except Exception as pin_err:
        print("Erro ao processar o Pin.", pin_err)


    # DYNAMORIO
    try:
        dynamorio_success = False
        dynamorio_path_zip = "dynamorio/dynamorio_run_data.json"
        decompress_dynamorio = decompress_specific_file(file_path, out_dir, dynamorio_path_zip)
        if decompress_dynamorio:
            dynamorio_out_path = os.path.join(out_dir, dynamorio_path_zip)
            with open(dynamorio_out_path, 'r') as file_dynamorio:
                data_dynamorio = json.load(file_dynamorio)
                dynamorio_success = bool(data_dynamorio["dynamorio_tool_success"])
                update_dynamorio_tool_success(sample_hash256_or_id, dynamorio_success)
    except Exception as dynamorio_err:
        print("Erro ao processar o Dynamorio.", dynamorio_err)


    # FRIDA
    try:
        frida_success = False
        frida_path_zip = "frida/frida.json"
        decompress_frida = decompress_specific_file(file_path, out_dir, frida_path_zip)
        if decompress_frida:
            frida_out_path = os.path.join(out_dir, frida_path_zip)
            with open(frida_out_path, 'r') as file_frida:
                data_frida = json.load(file_frida)
                frida_success = len(int(data_frida["functions_call_trace"])) > 5
                update_frida_tool_success(sample_hash256_or_id, bool(frida_success))
    except Exception as frida_err:
        print("Erro ao processar o Frida.", frida_err)


    # CAPA
    try:
        capa_path_zip = "capa/capa.json"
        decompress_capa = decompress_specific_file(file_path, out_dir, capa_path_zip)
        if decompress_capa:
            capa_out_path = os.path.join(out_dir, capa_path_zip)
            process_capa(sample_hash256_or_id, capa_out_path)
    except Exception as capa_err:
        print("Erro ao processar o Capa.", capa_err)

    # YARA
    try:
        yara_path_zip = "yara/yara.json"
        decompress_yara = decompress_specific_file(file_path, out_dir, yara_path_zip)
        if decompress_yara:
            yara_out_path = os.path.join(out_dir, yara_path_zip)
            process_yara(sample_hash256_or_id, yara_out_path)
    except Exception as yara_err:
        print("Erro ao processar o Yara.", yara_err)

    # DIE
    try:
        die_path_zip = "die/die_detects.json"
        decompress_die = decompress_specific_file(file_path, out_dir, die_path_zip)
        if decompress_die:
            die_out_path = os.path.join(out_dir, die_path_zip)
            process_die(sample_hash256_or_id, die_out_path)
    except Exception as die_err:
        print("Erro ao processar o Die.", die_err)

    update_sample_status(sample_hash256_or_id, 'processed')

def process_all_results(directory=None):
    if not directory:
        directory = "results"
    processed = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            process_result(item_path)
            processed.append(item)
    return processed
