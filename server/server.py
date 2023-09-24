import os
import tempfile
from flask import Flask, request, jsonify, send_file
from database import create_samples_table, create_config_table, insert_sample, get_samples, update_sample_status, remove_all_records, update_config, get_config
from run_analisys import run_analisys
from utils import compress_folder, select_host_ip, delete_all_files_and_folders
import threading

def create_app():
    create_samples_table()  
    create_config_table()
    app = Flask(__name__)
    app.config['TIMEOUT'] = 300

    select_host_ip()

    thread_analisys = threading.Thread(target=run_analisys, name='Thread Analisys')
    thread_analisys.daemon = True
    thread_analisys.start()

    @app.route('/')
    def index():
        return 'Criar lista de amostras em HTML'
    
    @app.route('/register', methods=['GET', 'POST'])
    def register_file():
        if request.method == 'POST':
        
            sample_hash = request.form.get('hash_sha256', '')
            insert_sample(sample_hash)
            return f'Arquivo com hash "{sample_hash}" registrado no banco de dados.'
        return '''
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="Enviar arquivo">
            </form>
        '''
    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            file = request.files['file']
            if file:
                filename = file.filename
                file.save(os.path.join("results", filename))

                sample_hash = request.form.get('hash_sha256', '')
                update_sample_status(sample_hash, 'processed')
                return f'Arquivo com hash "{sample_hash}" enviado e salvo no banco de dados.'
        return '''
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="Enviar arquivo">
            </form>
        '''

    @app.route('/samples', methods=['GET'])
    def get_samples_data():
        samples = get_samples()
        return jsonify(samples)

    @app.route('/clear-samples', methods=['GET'])
    def clear_samples():
        delete_all_files_and_folders("results")
        remove_all_records()
        return "Todos as amostras e registros foram removidos com sucesso" 
     
    @app.route('/download-agent')
    def download_agent():
        folder_path = '../agent' 
        temp_dir = "tmp"
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        
        output_filename = os.path.join(temp_dir, 'agent.zip')

        if not os.path.exists(output_filename):
            compress_folder(folder_path, output_filename)
        
        return send_file(output_filename, as_attachment=True)
    

    @app.route('/analisys', methods=['GET', 'POST'])
    def analisys():
        if request.method == 'POST':
            analysis_enabled = request.form.get('analysis_enabled', '0')
            update_config("analysis_enabled", analysis_enabled)
            vm_name = request.form.get('vm_name', '')
            update_config("vm_name", vm_name)
            snapshot_name = request.form.get('snapshot_name', '')
            update_config("snapshot_name", snapshot_name)

        analysis_enabled = get_config("analysis_enabled")
        if not analysis_enabled:
            analysis_enabled = '0'
        vm_name = get_config("vm_name")
        if not vm_name:
            vm_name = ''
        snapshot_name = get_config("snapshot_name")
        if not snapshot_name:
            snapshot_name = ''

        analysis_action = "1"
        button_text = 'Iniciar'
        if analysis_enabled == "1":
            analysis_action = "0"
            button_text = 'Parar'

        return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Controle de Análise</title>
            </head>
            <body>
                <h1>Controle de Análise</h1>
                <form method="POST" action="/analisys">
                    <input type="hidden" id="analysis_enabled" name="analysis_enabled" value="{analysis_action}"><br><br>

                    <label for="vm_name">Nome da VM:</label>
                    <input type="text" id="vm_name" name="vm_name" value="{vm_name}"><br><br>

                    <label for="snapshot_name">Nome do Snapshot:</label>
                    <input type="text" id="snapshot_name" name="snapshot_name" value="{snapshot_name}"><br><br>

                    <input type="submit" value="{button_text}">
                </form>
            </body>
            </html>
        '''
    
    @app.route('/disable-analisys', methods=['GET'])
    def disable_analisys():
        update_config("analysis_enabled", '0')
        return "Análise desativada"
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')