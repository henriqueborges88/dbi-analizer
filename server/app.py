from flask import Flask, request, jsonify, send_file, render_template, abort
from controllers.sample_controller import (insert_sample, get_all_samples, update_sample_status, remove_all_samples)
from controllers.config_controller import (update_config_item, get_config_item)
from utils import compress_folder, delete_all_files_and_folders, ensure_directory_exists, write_ip_to_file
import os
import re
import zipfile
import threading
from run_analysis import run_analysis
from virtualbox_manager import configure_hostonly_network
from models import db
from flask_migrate import Migrate
from models import *
from process_result import process_result, process_all_results
from models import Sample
from collections import Counter, defaultdict

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
thread_analysis = threading.Thread(target=run_analysis, name='Thread Analysis', args=[app, SERVER_IP], daemon=True)
thread_analysis.start()

@app.route('/')
def index():
    # Aqui, exibir uma lista de amostras ou alguma outra informação relevante.
    return 'Bem-vindo ao sistema de gestão de amostras.'


def normalized_sample_hash(value):
    if not re.fullmatch(r'[a-fA-F0-9]{64}', value or ''):
        abort(400, description='Informe um hash SHA-256 válido, com 64 caracteres hexadecimais.')
    return value.lower()

@app.route('/register', methods=['GET', 'POST'])
def register_sample():
    if request.method == 'POST':
        sample_hash = normalized_sample_hash(request.form.get('hash_sha256'))
        if insert_sample(sample_hash):
            return jsonify(message='Hash registrado com sucesso.', hash_sha256=sample_hash)
        return jsonify(message='Hash já existe.', hash_sha256=sample_hash)
    return render_template('samples/register_sample.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        sample_hash = normalized_sample_hash(request.form.get('hash_sha256'))
        if not file:
            abort(400, description='Envie o arquivo ZIP dos resultados.')
        if not zipfile.is_zipfile(file.stream):
            abort(400, description='O arquivo enviado deve ser um ZIP válido.')
        file.stream.seek(0)
        results_directory = ensure_directory_exists(app.config.get('RESULTS_DIRECTORY', 'results'))
        filename = f'{sample_hash}.zip'
        result_path = os.path.join(results_directory, filename)
        if Sample.query.filter_by(hash_sha256=sample_hash).first() is None:
            insert_sample(sample_hash)
        file.save(result_path)
        process_result(result_path)
        return jsonify(message='Resultados recebidos.', filename=filename, hash_sha256=sample_hash)
    return render_template('samples/upload_file.html')

@app.route('/samples', methods=['GET'])
def get_samples():
    samples = get_all_samples()
    return jsonify([{'hash_sha256': sample.hash_sha256, 'status': sample.status} for sample in samples])

@app.route('/sample/details/<hash_sha256>', methods=['GET'])
def sample_details(hash_sha256):
    sample = Sample.query.filter_by(hash_sha256=hash_sha256).first()

    if sample is None:
        abort(404)

    die_infos = sample.die_infos
    yara_infos = sample.yara_infos
    capa_infos = sample.capa_infos

    return render_template('samples/sample_details.html',
                           sample=sample,
                           die_infos=die_infos,
                           yara_infos=yara_infos,
                           capa_infos=capa_infos)

@app.route('/sample/list', methods=['GET'])
def sample_list_tools():
    tool_name = request.args.get('tool_name')
    field = request.args.get('field')
    rule = request.args.get('rule')

    query = Sample.query
    filtr = 'todas'
    if any(value is not None for value in (tool_name, field, rule)):
        detection_filters = {
            ('capa', 'name'): (CapaInfo, CapaInfo.name),
            ('capa', 'namespace'): (CapaInfo, CapaInfo.namespace),
            ('yara', 'rule'): (YaraInfo, YaraInfo.rule),
            ('yara', 'namespace'): (YaraInfo, YaraInfo.namespace),
            ('die', 'name'): (DieInfo, DieInfo.name),
            ('die', 'type'): (DieInfo, DieInfo.type),
        }
        instrumentation_filters = {
            'pin': Sample.pin_tool_success,
            'frida': Sample.frida_tool_success,
            'dynamorio': Sample.dynamorio_tool_success,
        }
        if not tool_name or not field or rule is None or rule == '':
            abort(404)
        if (tool_name, field) in detection_filters:
            model, column = detection_filters[(tool_name, field)]
            query = query.join(model).filter(column == rule).distinct()
        elif tool_name in instrumentation_filters and field == 'result' and rule in ('success', 'fail'):
            column = instrumentation_filters[tool_name]
            query = query.filter(column.is_(True) if rule == 'success' else column.is_not(True))
        else:
            abort(404)
        filtr = f'{tool_name.capitalize()} > {field.capitalize()} > {rule}'

    samples = query.order_by(Sample.hash_sha256).all()
    return render_template(
        'samples/samples.html',
        samples=samples,
        filtr=filtr,
        samples_pin_success_freq=sum(bool(sample.pin_tool_success) for sample in samples),
        samples_pin_not_success_freq=sum(not sample.pin_tool_success for sample in samples),
        samples_dynamorio_success_freq=sum(bool(sample.dynamorio_tool_success) for sample in samples),
        samples_dynamorio_not_success_freq=sum(not sample.dynamorio_tool_success for sample in samples),
        samples_frida_success_freq=sum(bool(sample.frida_tool_success) for sample in samples),
        samples_frida_not_success_freq=sum(not sample.frida_tool_success for sample in samples),
    )


def detection_frequencies(infos, field, prefix):
    occurrences = Counter()
    sample_hashes = defaultdict(set)
    for info in infos:
        value = getattr(info, field)
        if value:
            occurrences[value] += 1
            sample_hashes[value].add(info.sample_hash_sha256)
    return {
        value: {
            f'{prefix}_sample_freq': len(sample_hashes[value]),
            f'{prefix}_freq': count,
        }
        for value, count in sorted(occurrences.items())
    }


@app.route('/sample/tools', methods=['GET'])
def sample_tools():
    die_infos = DieInfo.query.all()
    yara_infos = YaraInfo.query.all()
    capa_infos = CapaInfo.query.all()
    capa_name_categories = defaultdict(set)
    for info in capa_infos:
        if info.name and info.namespace:
            capa_name_categories[info.name].add(info.namespace)

    return render_template(
        'samples/samples_tools.html',
        die_name=detection_frequencies(die_infos, 'name', 'die_name'),
        die_type=detection_frequencies(die_infos, 'type', 'die_type'),
        yara_rule=detection_frequencies(yara_infos, 'rule', 'yara_rule'),
        yara_namespace=detection_frequencies(yara_infos, 'namespace', 'yara_namespace'),
        capa_name=detection_frequencies(capa_infos, 'name', 'capa_name'),
        capa_namespace=detection_frequencies(capa_infos, 'namespace', 'capa_namespace'),
        capa_name_categories=capa_name_categories,
    )


@app.route('/process-all-samples', methods=['GET'])
def process_all_samples():
    precessed_results = process_all_results(app.config.get('RESULTS_DIRECTORY', 'results'))
    return jsonify(precessed_results)

@app.route('/clear-samples', methods=['GET'])
def clear_samples():
    delete_all_files_and_folders(app.config.get('RESULTS_DIRECTORY', 'results'))
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
