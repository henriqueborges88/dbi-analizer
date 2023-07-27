import hashlib
import zipfile
import os

def calculate_sha256_hash(file_path):
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(block)

    # Return the hexadecimal representation of the SHA-256 hash
    return sha256_hash.hexdigest()


def compress_folder(source_folder, zip_file):
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for current_folder, _, files in os.walk(source_folder):
            for file in files:
                full_path = os.path.join(current_folder, file)

                relative_path = os.path.relpath(full_path, source_folder)

                zipf.write(full_path, relative_path)

