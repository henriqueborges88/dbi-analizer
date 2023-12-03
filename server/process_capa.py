import json
import sys
from models import db, CapaInfo, Sample


def extract_capa_info(file_path):
    capa_rules = []
    with open (file_path, "r") as file:
        capa_info = json.load(file)
        for key, value in capa_info["rules"].items():
            rule = value
            info = {
                "name": rule.get("meta", {}).get("name", key),
                "authors": "; ".join(rule.get("meta", {}).get("authors")),
                "scope": rule.get("meta", {}).get("scope", ""),
                "references": "; ".join(rule.get("meta", {}).get("references")),
                "description": rule.get("meta", {}).get("description", ""),
                "namespace": rule.get("meta", {}).get("namespace", ""),
            }
            capa_rules.append(info)
    return capa_rules


def process_capa(sample_hash_sha256, capa_path):
    sample = Sample.query.get(sample_hash_sha256)
    if sample:
        CapaInfo.query.filter_by(sample_hash_sha256=sample.hash_sha256).delete()
        db.session.commit()
    else:
        print("Amostra não encontrada")
        return

    capa_info_arr = extract_capa_info(capa_path)
    for capa_info in capa_info_arr:
        new_capa_info = CapaInfo(
            sample_hash_sha256=sample_hash_sha256,
            name=capa_info["name"],
            authors=capa_info["authors"],
            scope=capa_info["scope"],
            references=capa_info["references"],
            description=capa_info["description"],
            namespace=capa_info["namespace"]
        )
        db.session.add(new_capa_info)

    db.session.commit()


def main():
    if len(sys.argv) < 2:
        print("Uso: python process_capa.py <arquivo>")
        #return 
    file_path = sys.argv[1]
    capa_info = extract_capa_info(file_path)
    print(capa_info)

if __name__ == "__main__":
    main()