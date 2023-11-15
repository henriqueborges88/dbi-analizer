from flask import Flask, request, jsonify, send_file, render_template
from controllers import (insert_sample, get_all_samples, update_sample_status,
                         update_config_item, get_config_item, remove_all_samples)
from utils import compress_folder, delete_all_files_and_folders, write_ip_to_file
import os
import threading
from run_analysis import run_analysis
from virtualbox_manager import configure_hostonly_network
from models import db
from flask_migrate import Migrate

SERVER_IP="192.168.56.10"

app = Flask(__name__)
app.config['TIMEOUT'] = 300

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'malware_data.db')
db.init_app(app)
with app.app_context():
    db.create_all()
migrate = Migrate(app, db)

configure_hostonly_network(SERVER_IP)
write_ip_to_file(SERVER_IP)

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
    return render_template('register_sample.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        sample_hash = request.form.get('hash_sha256')
        if file and sample_hash:
            filename = file.filename
            file.save(os.path.join('results', filename))
            update_sample_status(sample_hash, 'processed')
            return f'Arquivo "{filename}" com hash "{sample_hash}" foi enviado.'
        return 'Nenhum arquivo enviado.'
    return render_template('upload_file.html')

@app.route('/samples', methods=['GET'])
def get_samples_data():
    samples = get_all_samples()
    return jsonify([{'id': sample.id, 'hash': sample.sample_hash_sha256, 'status': sample.status} for sample in samples])

@app.route('/clear-samples', methods=['GET'])
def clear_samples():
    delete_all_files_and_folders('results')
    remove_all_samples()
    return 'Todos as amostras e registros foram removidos com sucesso.'

@app.route('/download-agent')
def download_agent():
    folder_path = '../agent'
    temp_dir = 'tmp'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
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
    return render_template('analysis.html', analysis_action=analysis_action, vm_name=vm_name, snapshot_name=snapshot_name, button_text=button_text)

@app.route('/disable-analysis', methods=['GET'])
def disable_analysis():
    update_config_item('analysis_enabled', '0')
    return 'Análise desativada.'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
