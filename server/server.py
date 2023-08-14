import os
import tempfile
from flask import Flask, request, jsonify, send_file
from database import create_table, insert_sample, get_samples, update_sample_status
from utils import zip_folder, select_host_ip

def create_app():
    create_table()  # Chamada da função para criar a tabela
    app = Flask(__name__)
    app.config['TIMEOUT'] = 300

    select_host_ip()

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
        
    @app.route('/download_agent')
    def download_agent():
        folder_path = '../agent'  # Substitua pelo caminho da pasta que deseja compactar
        temp_dir = "tmp"
        output_filename = os.path.join(temp_dir, 'agent')

        if not os.path.exists(output_filename):
            zip_folder(folder_path, output_filename)
        
        return send_file(output_filename + '.zip', as_attachment=True)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')