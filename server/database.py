import os
import sqlite3

DB_NAME = "malware_data.db"

def create_samples_table():
   
    conn = sqlite3.connect(DB_NAME)
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



def check_if_sample_exists(sample_hash_sha256):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar se o hash já existe na tabela
    cursor.execute('SELECT COUNT(*) FROM samples WHERE sample_hash_sha256 = ?', (sample_hash_sha256,))
    count = cursor.fetchone()[0]

    conn.close()

    return count > 0

def insert_sample(sample_hash_sha256):
    if not check_if_sample_exists(sample_hash_sha256):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Inserir o novo registro na tabela
        cursor.execute('INSERT INTO samples (sample_hash_sha256) VALUES (?)', (sample_hash_sha256,))

        conn.commit()
        conn.close()
        print(f"Hash '{sample_hash_sha256}' inserido com sucesso.")
    else:
        print(f"Hash '{sample_hash_sha256}' já existe na tabela e não será inserido.")


def update_sample_status(sample_hash_sha256, new_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Executar a atualização
    update_query = "UPDATE samples SET status = ? WHERE sample_hash_sha256 = ?"
    cursor.execute(update_query, (new_status, sample_hash_sha256))

    conn.commit()
    conn.close()


def get_samples():
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Remover todos os registros da tabela
    cursor.execute('DELETE FROM samples')

    conn.commit()
    conn.close()
    
    
def create_config_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Criar a tabela se ainda não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            config_name TEXT NOT NULL,
            config_value TEXT
        )
    ''')

    conn.commit()
    conn.close()



def get_config(config_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM config WHERE config_name = ?', (config_name,))
    existing_record = cursor.fetchone()
    conn.close()

    if existing_record is None:
        return None
    else:
        return existing_record[1]


def update_config(config_name, config_value):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM config WHERE config_name = ?', (config_name,))
    existing_record = cursor.fetchone()

    if existing_record is None:
        cursor.execute('INSERT INTO config (config_name, config_value) VALUES (?, ?)', (config_name, config_value))
        conn.commit()
    else:
        cursor.execute('UPDATE config SET config_value = ? WHERE config_name = ?', (config_value, config_name))
        conn.commit()

    conn.close()