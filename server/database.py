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
            sample_name TEXT NOT NULL,
            sample_hash_sha256 TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def insert_sample(sample_name, sample_hash_sha256):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Inserir o novo registro na tabela
    cursor.execute('INSERT INTO samples (sample_name, sample_hash_sha256) VALUES (?, ?)', (sample_name, sample_hash_sha256))

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
            'sample_name': row[1],
            'sample_hash_sha256': row[2]
        }
        samples.append(sample)

    conn.close()
    return samples