from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Sample, DieInfo, YaraInfo, CapaInfo
import os 

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'malware_data.db'), echo=True)

Session = sessionmaker(bind=engine)
session = Session()

def remove_invalid_samples():
    invalid_samples = session.query(Sample).filter(
        (Sample.status == 'registered') |
        (Sample.pin_tool_success == False) |
        (Sample.dynamorio_tool_success == False) |
        (Sample.frida_tool_success == False)
    ).all()

    for sample in invalid_samples:
        session.query(DieInfo).filter(DieInfo.sample_hash_sha256 == sample.hash_sha256).delete()
        session.query(YaraInfo).filter(YaraInfo.sample_hash_sha256 == sample.hash_sha256).delete()
        session.query(CapaInfo).filter(CapaInfo.sample_hash_sha256 == sample.hash_sha256).delete()
        
        session.delete(sample)
        print(f'Removido: {sample}')

    session.commit()

if __name__ == '__main__':
    remove_invalid_samples()
