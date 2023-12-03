import json
import sys
from models import db, DieInfo, Sample


def extract_die_info(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    detects = []
    for detect in data['detects']:
        # Se 'values' estiver presente, iteramos por cada valor
        if 'values' in detect:
            for value in detect['values']:
                row = {
                    'filetype': detect.get('filetype', ''),
                    'parentfilepart': detect.get('parentfilepart', ''),
                    'info': value.get('info', ''),
                    'name': value.get('name', ''),
                    'string': value.get('string', ''),
                    'type': value.get('type', ''),
                    'version': value.get('version', '')
                }
                detects.append(row)
        else:
            # Se 'values' não estiver presente, apenas adicionamos o detect atual
            detect['filetype'] = detect.get('filetype', '')
            detect['parentfilepart'] = detect.get('parentfilepart', '')
            detects.append(detect)

    return detects


def process_die(sample_hash_sha256, die_path):
    sample = Sample.query.get(sample_hash_sha256)
    if sample:
        DieInfo.query.filter_by(sample_hash_sha256=sample.hash_sha256).delete()
        db.session.commit()
    else:
        print("Amostra não encontrada")
        return

    die_info_arr = extract_die_info(die_path)
    for die_info in die_info_arr:
        new_die_info = DieInfo(
            sample_hash_sha256=sample_hash_sha256,
            filetype=die_info["filetype"],
            parentfilepart=die_info["parentfilepart"],
            info=die_info["info"],
            name=die_info["name"],
            string=die_info["string"],
            type=die_info["type"],
            version=die_info["version"]
        )
        db.session.add(new_die_info)

    db.session.commit()


def main():
    if len(sys.argv) < 2:
        print("Uso: python process_die.py <arquivo>")
        #return 
    file_path = sys.argv[1]
    capa_info = extract_die_info(file_path)
    print(capa_info)

if __name__ == "__main__":
    main()