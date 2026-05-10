import hashlib
import os


def sha256_file(path, chunk_size=1024 * 1024):
    hash_sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()


def build_checksums(folder):
    results = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, folder)

            try:
                checksum = sha256_file(file_path)
                results.append({
                    "path": rel_path,
                    "sha256": checksum
                })
            except Exception as e:
                results.append({
                    "path": rel_path,
                    "sha256": None,
                    "error": str(e)
                })

    return results


def write_checksum_file(checksums, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for item in checksums:
            if item.get("sha256"):
                f.write(f"{item['sha256']}  {item['path']}\n")
            else:
                f.write(f"ERROR  {item['path']}  {item.get('error')}\n")
