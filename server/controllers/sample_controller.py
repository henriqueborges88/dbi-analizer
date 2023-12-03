from models import db, Sample, Config

def insert_sample(sample_hash):
    existing_sample = Sample.query.filter_by(hash_sha256=sample_hash).first()
    if not existing_sample:
        new_sample = Sample(hash_sha256=sample_hash)
        db.session.add(new_sample)
        db.session.commit()
        return new_sample.hash_sha256
    return None

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

def update_pin_tool_success(sample_hash, success):
    sample = Sample.query.filter_by(hash_sha256=sample_hash).first()
    if sample:
        sample.pin_tool_success = success
        db.session.commit()
        return sample.hash_sha256
    return None

def update_dynamorio_tool_success(sample_hash, success):
    sample = Sample.query.filter_by(hash_sha256=sample_hash).first()
    if sample:
        sample.dynamorio_tool_success = success
        db.session.commit()
        return sample.hash_sha256
    return None

def update_frida_tool_success(sample_hash, success):
    sample = Sample.query.filter_by(hash_sha256=sample_hash).first()
    if sample:
        sample.frida_tool_success = success
        db.session.commit()
        return sample.hash_sha256
    return None

def update_sample_status(sample_hash, status):
    sample = Sample.query.filter_by(hash_sha256=sample_hash).first()
    if sample:
        sample.status = status
        db.session.commit()
        return sample.hash_sha256
    return None

