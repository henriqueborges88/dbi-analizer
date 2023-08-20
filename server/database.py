import os
import sqlite3

db_name = "malware_data.db"
def create_table():
   
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Criar a tabela se ainda não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_hash_sha256 TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'registered'
            )
    ''')

    conn.commit()
    conn.close()

def insert_sample(sample_hash_sha256):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Inserir o novo registro na tabela
    cursor.execute('INSERT INTO samples (sample_hash_sha256) VALUES (?)', (sample_hash_sha256,))

    conn.commit()
    conn.close()

def update_sample_status(sample_hash_sha256, new_status):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Executar a atualização
    update_query = "UPDATE samples SET status = ? WHERE sample_hash_sha256 = ?"
    cursor.execute(update_query, (new_status, sample_hash_sha256))

    conn.commit()
    conn.close()


def get_samples():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM samples')
    rows = cursor.fetchall()

    samples = []
    for row in rows:
        sample = {
            'id': row[0],
            'sample_hash_sha256': row[1],
            'status': row[2]
        }
        samples.append(sample)

    conn.close()
    return samples

def remove_all_records():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Remover todos os registros da tabela
    cursor.execute('DELETE FROM samples')

    conn.commit()
    conn.close()