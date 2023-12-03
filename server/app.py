from flask import Flask, request, jsonify, send_file, render_template
from controllers.sample_controller import (insert_sample, get_all_samples, update_sample_status, remove_all_samples)
from controllers.config_controller import (update_config_item, get_config_item)
from utils import compress_folder, delete_all_files_and_folders, ensure_directory_exists, write_ip_to_file
import os
import threading
from run_analysis import run_analysis
from virtualbox_manager import configure_hostonly_network
from models import db
from flask_migrate import Migrate
from models import *
from process_result import process_result, process_all_results
from models import Sample
from collections import Counter

SERVER_IP="192.168.56.10"

app = Flask(__name__)
app.config['TIMEOUT'] = 300

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'malware_data.db')
db.init_app(app)

# When use flask_migrate to create database structure comment db.create_all()
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

write_ip_to_file(SERVER_IP)

configure_hostonly_network(SERVER_IP)
thread_analisys = threading.Thread(target=run_analysis, name='Thread Analisys', args=[app, SERVER_IP], daemon=True)
thread_analisys.start()

@app.route('/')
def index():
    # Aqui, exibir uma lista de amostras ou alguma outra informação relevante.
    return 'Bem-vindo ao sistema de gestão de amostras.'

@app.route('/register', methods=['GET', 'POST'])
def register_sample():
    if request.method == 'POST':
        sample_hash = request.form.get('hash_sha256')
        if insert_sample(sample_hash):
            return f'Hash "{sample_hash}" registrado com sucesso.'
        return f'Hash "{sample_hash}" já existe.'
    return render_template('samples/register_sample.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        sample_hash = request.form.get('hash_sha256')
        if file and sample_hash:
            filename = file.filename
            ensure_directory_exists('results')
            result_path = os.path.join('results', filename)
            sample = Sample.query.get(sample_hash)
            if not sample:
                if not insert_sample(sample_hash):
                    raise Exception(f"Não foi possével regustrar a amostra {sample_hash}")
            file.save(result_path)
            process_result(result_path)
            return f'Arquivo "{filename}" com hash "{sample_hash}" foi enviado.'
        return 'Nenhum arquivo enviado.'
    return render_template('samples/upload_file.html')

@app.route('/samples', methods=['GET'])
def get_samples():
    samples = get_all_samples()
    return jsonify([{'hash_sha256': sample.hash_sha256, 'status': sample.status} for sample in samples])

@app.route('/sample/list', methods=['GET'])
def get_samples_data():
    samples = get_all_samples()

    samples_pin_success_freq = len([sample.pin_tool_success for sample in samples if sample.pin_tool_success == True])
    samples_pin_not_success_freq = len([sample.pin_tool_success for sample in samples if sample.pin_tool_success == False])

    samples_dynamorio_success_freq = len([sample.dynamorio_tool_success for sample in samples if sample.dynamorio_tool_success == True])
    samples_dynamorio_not_success_freq = len([sample.dynamorio_tool_success for sample in samples if sample.dynamorio_tool_success == False])

    samples_frida_success_freq = len([sample.frida_tool_success for sample in samples if sample.frida_tool_success == True])
    samples_frida_not_success_freq = len([sample.frida_tool_success for sample in samples if sample.frida_tool_success == False])

    die_infos = DieInfo.query.all()
    die_name_freq = Counter([info.name for info in die_infos if info.name is not None and info.name != ""])
    die_type_freq = Counter([info.type for info in die_infos if info.type is not None and info.type != ""])

    yara_infos = YaraInfo.query.all()
    yara_rule_freq = Counter([info.rule for info in yara_infos if info.rule is not None and info.rule != ""])
    yara_namespace_freq = Counter([info.namespace for info in yara_infos if info.namespace is not None and info.namespace != ""])

    capa_infos = CapaInfo.query.all()
    capa_name_freq = Counter([info.name for info in capa_infos if info.name is not None and info.name != ""])
    capa_namespace_freq = Counter([info.namespace for info in capa_infos if info.namespace is not None and info.namespace != ""])

    return render_template('samples/samples.html', samples=samples, 
                            samples_pin_success_freq=samples_pin_success_freq,
                            samples_pin_not_success_freq=samples_pin_not_success_freq,
                            samples_dynamorio_success_freq=samples_dynamorio_success_freq,
                            samples_dynamorio_not_success_freq=samples_dynamorio_not_success_freq,
                            samples_frida_success_freq=samples_frida_success_freq,
                            samples_frida_not_success_freq=samples_frida_not_success_freq,
                            die_name_freq=die_name_freq, die_type_freq=die_type_freq,
                            yara_rule_freq=yara_rule_freq, yara_namespace_freq=yara_namespace_freq,
                            capa_name_freq=capa_name_freq, capa_namespace_freq=capa_namespace_freq)

@app.route('/sample/details/<hash_sha256>', methods=['GET'])
def sample_details(hash_sha256):
    sample = Sample.query.filter_by(hash_sha256=hash_sha256).first()

    if sample is None:
        abort(404)

    die_infos = sample.die_infos
    yara_infos = sample.yara_infos
    capa_infos = sample.capa_infos

    return render_template('samples/sample_details.html', sample=sample, 
                           die_infos=die_infos, yara_infos=yara_infos, 
                           capa_infos=capa_infos)

@app.route('/process-all-samples', methods=['GET'])
def process_all_samples():
    precessed_results = process_all_results()
    return jsonify(precessed_results)

@app.route('/clear-samples', methods=['GET'])
def clear_samples():
    delete_all_files_and_folders('results')
    remove_all_samples()
    return 'Todos as amostras e registros foram removidos com sucesso.'

@app.route('/download-agent')
def download_agent():
    folder_path = '../agent'
    temp_dir = 'tmp'
    ensure_directory_exists(temp_dir)
    output_filename = os.path.join(temp_dir, 'agent.zip')
    if not os.path.exists(output_filename):
        compress_folder(folder_path, output_filename)
    return send_file(output_filename, as_attachment=True)

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        analysis_enabled = request.form.get('analysis_enabled')
        vm_name = request.form.get('vm_name')
        snapshot_name = request.form.get('snapshot_name')
        update_config_item('analysis_enabled', analysis_enabled)
        update_config_item('vm_name', vm_name)
        update_config_item('snapshot_name', snapshot_name)
    analysis_enabled = get_config_item('analysis_enabled') or '0'
    vm_name = get_config_item('vm_name') or ''
    snapshot_name = get_config_item('snapshot_name') or ''
    analysis_action = "1"
    button_text = 'Iniciar'
    if analysis_enabled == "1":
        analysis_action = "0"
        button_text = 'Parar'

    return render_template('analysis/analysis.html', analysis_action=analysis_action, vm_name=vm_name, snapshot_name=snapshot_name, button_text=button_text)

@app.route('/disable-analysis', methods=['GET'])
def disable_analysis():
    update_config_item('analysis_enabled', '0')
    return 'Análise desativada.'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
