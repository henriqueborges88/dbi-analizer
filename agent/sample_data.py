import requests

class SampleUploader:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def get_sample_list(self):
        url = f'{self.base_url}/samples'

        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Erro ao comunicar com o servidor")

    def upload_sample_data_file(self, file_path, hash_sha256_value):
        url = f'{self.base_url}/upload'

        files = {'file': open(file_path, 'rb')}
        data = {'hash_sha256': hash_sha256_value}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print('Arquivo enviado com sucesso e registrado no banco de dados.')
        else:
            print('Erro ao enviar o arquivo.')
