import json
import sys
from models import db, YaraInfo, Sample


def extract_yara_info(file_path):
    matches_info = []
    with open(file_path, "r") as file:
        data = json.load(file)
        for match in data["matches"]:
            info = {
                "rule": match.get("rule", ""),
                "author": match.get("author", ""),
                "original_author": match.get("original_author", ""),
                "reference": match.get("reference", match.get("source", "")),
                "tags": "; ".join(match.get("tags", [])),
                "namespace": match.get("namespace", ""),
                "description": match.get("description", ""),
                "date": match.get("date", "")
            }
            matches_info.append(info)
    return matches_info


def process_yara(sample_hash_sha256, yara_path):
    sample = Sample.query.get(sample_hash_sha256)
    if sample:
        YaraInfo.query.filter_by(sample_hash_sha256=sample.hash_sha256).delete()
        db.session.commit()
    else:
        print("Amostra não encontrada")
        return

    yara_info_arr = extract_yara_info(yara_path)
    for yara_info in yara_info_arr:
        new_yara_info = YaraInfo(
            sample_hash_sha256=sample_hash_sha256,
            rule=yara_info["rule"],
            author=yara_info["author"],
            original_author=yara_info["original_author"],
            reference=yara_info["reference"],
            tags=yara_info["tags"],
            namespace=yara_info["namespace"],
            description=yara_info["description"],
            date=yara_info["date"]
        )
        db.session.add(new_yara_info)

    db.session.commit()


def main():
    if len(sys.argv) < 2:
        print("Uso: python process_yara.py <arquivo>")
        #return 
    file_path = sys.argv[1]
    capa_info = extract_yara_info(file_path)
    print(capa_info)

if __name__ == "__main__":
    main()