import os
import json
import time
import subprocess
from datetime import datetime

from config import (
    MOUNT_BASE,
    MASTER_VOLUME_NAME,
    RUSHES_FOLDER,
    REPORTS_FOLDER,
)
from disk_utils import get_source_disks, get_master_disk, get_folder_size, format_bytes
from checksum import build_checksums, write_checksum_file


STATE = {
    "status": "idle",
    "running": False,
    "current_disk": None,
    "logs": [],
    "last_report": None,
    "error": None,
    "progress": 0,
}


def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    STATE["logs"].append(entry)
    print(entry)


def reset_state():
    STATE["status"] = "running"
    STATE["running"] = True
    STATE["current_disk"] = None
    STATE["logs"] = []
    STATE["last_report"] = None
    STATE["error"] = None
    STATE["progress"] = 0


def rsync_copy(source_path, dest_path):
    """Copie via rsync avec vérification de checksum."""
    os.makedirs(dest_path, exist_ok=True)
    cmd = [
        "rsync",
        "-avh",
        "--checksum",
        "--progress",
        f"{source_path}/",
        f"{dest_path}/",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr


def verify_copy(source_path, dest_path):
    """Vérifie que tous les fichiers source sont présents dans la destination."""
    missing = []
    mismatch = []

    for root, dirs, files in os.walk(source_path):
        for file in files:
            src_file = os.path.join(root, file)
            rel = os.path.relpath(src_file, source_path)
            dst_file = os.path.join(dest_path, rel)

            if not os.path.exists(dst_file):
                missing.append(rel)
                continue

            if os.path.getsize(src_file) != os.path.getsize(dst_file):
                mismatch.append(rel)

    return missing, mismatch


def start_ingest(project_name=None):
    reset_state()
    start_time = time.time()

    try:
        sources = get_source_disks()
        master = get_master_disk()

        if not master:
            raise RuntimeError("Disque MASTER introuvable. Brancher et nommer le SSD MASTER.")

        if not sources:
            raise RuntimeError("Aucun disque source détecté. Brancher au moins un SSD caméra.")

        required_space = sum(get_folder_size(disk["path"]) for disk in sources)

        if master["free"] < required_space:
            raise RuntimeError(
                f"Espace insuffisant sur MASTER. "
                f"Requis : {format_bytes(required_space)}, "
                f"Disponible : {format_bytes(master['free'])}"
            )

        if not project_name:
            project_name = datetime.now().strftime("%Y-%m-%d") + " - PROJET"

        project_root = os.path.join(master["path"], project_name)
        rushes_root = os.path.join(project_root, RUSHES_FOLDER)
        reports_root = os.path.join(project_root, REPORTS_FOLDER)

        for folder in [
            rushes_root,
            os.path.join(project_root, "02_AUDIO"),
            os.path.join(project_root, "03_PROXIES"),
            os.path.join(project_root, "04_PROJECT"),
            os.path.join(project_root, "05_EXPORTS"),
            reports_root,
        ]:
            os.makedirs(folder, exist_ok=True)

        report = {
            "project_name": project_name,
            "started_at": datetime.now().isoformat(),
            "finished_at": None,
            "duration_seconds": None,
            "success": False,
            "required_space_bytes": required_space,
            "required_space_human": format_bytes(required_space),
            "master_disk": master["name"],
            "sources": [],
        }

        all_checksums = []
        total_disks = len(sources)

        for idx, disk in enumerate(sources):
            disk_name = disk["name"]
            STATE["current_disk"] = disk_name
            STATE["progress"] = int((idx / total_disks) * 100)

            log(f"Copie de {disk_name} ({format_bytes(get_folder_size(disk['path']))})")

            destination = os.path.join(rushes_root, disk_name)

            success, stdout, stderr = rsync_copy(disk["path"], destination)

            if not success:
                log(f"  ERREUR rsync pour {disk_name}: {stderr.strip()}")

            missing, mismatch = verify_copy(disk["path"], destination)
            disk_success = success and not missing and not mismatch

            log(f"  Calcul checksums {disk_name}…")
            destination_checksums = build_checksums(destination)

            report["sources"].append({
                "name": disk_name,
                "source_path": disk["path"],
                "destination_path": destination,
                "size_bytes": get_folder_size(disk["path"]),
                "success": disk_success,
                "missing_files": missing,
                "checksum_mismatch": mismatch,
            })

            for item in destination_checksums:
                all_checksums.append({
                    "path": os.path.join(RUSHES_FOLDER, disk_name, item["path"]),
                    "sha256": item["sha256"],
                })

            if disk_success:
                log(f"  OK : {disk_name}")
            else:
                log(f"  ERREUR : {disk_name}")

        STATE["progress"] = 95

        report["finished_at"] = datetime.now().isoformat()
        report["duration_seconds"] = round(time.time() - start_time, 2)
        report["success"] = all(source["success"] for source in report["sources"])

        json_report_path = os.path.join(reports_root, "ingest_report.json")
        txt_report_path = os.path.join(reports_root, "ingest_report.txt")
        checksums_path = os.path.join(reports_root, "checksums.sha256")

        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        with open(txt_report_path, "w", encoding="utf-8") as f:
            f.write(f"Projet: {project_name}\n")
            f.write(f"Succès: {report['success']}\n")
            f.write(f"Durée: {report['duration_seconds']} secondes\n")
            f.write(f"Espace copié: {report['required_space_human']}\n\n")
            for source in report["sources"]:
                f.write(f"{source['name']}: {'OK' if source['success'] else 'ERROR'}\n")
                if source["missing_files"]:
                    f.write(f"  Fichiers manquants: {source['missing_files']}\n")
                if source["checksum_mismatch"]:
                    f.write(f"  Checksums incorrects: {source['checksum_mismatch']}\n")

        write_checksum_file(all_checksums, checksums_path)

        STATE["last_report"] = report
        STATE["progress"] = 100
        STATE["status"] = "complete" if report["success"] else "complete_with_errors"
        log("Ingest terminé.")

    except Exception as e:
        STATE["error"] = str(e)
        STATE["status"] = "error"
        log(f"ERREUR FATALE : {e}")

    finally:
        STATE["running"] = False
        STATE["current_disk"] = None
