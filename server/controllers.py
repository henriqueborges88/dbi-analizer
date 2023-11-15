from models import db, Sample, Config

def insert_sample(sample_hash):
    existing_sample = Sample.query.filter_by(sample_hash_sha256=sample_hash).first()
    if not existing_sample:
        new_sample = Sample(sample_hash_sha256=sample_hash)
        db.session.add(new_sample)
        db.session.commit()
        return True
    return False

def get_all_samples():
    return Sample.query.all()

def remove_all_samples():
    try:
        num_rows_deleted = db.session.query(Sample).delete()
        db.session.commit()
        return num_rows_deleted
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao tentar remover todas as amostras: {e}")
        return 0

def update_sample_status(sample_hash, status):
    sample = Sample.query.filter_by(sample_hash_sha256=sample_hash).first()
    if sample:
        sample.status = status
        db.session.commit()
        return True
    return False

def update_config_item(name, value):
    config_item = Config.query.filter_by(config_name=name).first()
    if config_item:
        config_item.config_value = value
    else:
        config_item = Config(config_name=name, config_value=value)
        db.session.add(config_item)
    db.session.commit()

def get_config_item(name):
    config_item = Config.query.filter_by(config_name=name).first()
    if config_item:
        return config_item.config_value
    return None
