import os
import re
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
    "cancelled": False,
    "current_disk": None,
    "current_disk_index": 0,
    "total_disks": 0,
    "current_file": None,
    "speed": None,
    "eta": None,
    "disk_progress": 0,
    "total_progress": 0,
    "bytes_transferred": 0,
    "bytes_total": 0,
    "files_done": 0,
    "files_total": 0,
    "elapsed_seconds": 0,
    "logs": [],
    "last_report": None,
    "error": None,
}

# Référence au process rsync en cours (pour pouvoir l'annuler)
_current_process = None

# Regex pour parser la ligne de progression rsync --info=progress2
# Ex:  1,234,567  45%   12.34MB/s    0:00:10
_PROGRESS_RE = re.compile(
    r"([\d,]+)\s+(\d+)%\s+([\d.]+\s*\S+/s)\s+([\d:]+|\-\-:--:--)"
)
# Regex pour détecter le nom de fichier courant dans la sortie rsync
_FILE_RE = re.compile(r"^(?!\s)(.+\.(mp4|mov|mxf|r3d|braw|ari|mts|mpeg|avi|dng|jpg|jpeg|png|wav|aiff|aif|mp3))\s*$", re.IGNORECASE)


def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    STATE["logs"].append(entry)
    print(entry)


def cancel_ingest():
    """Annule l'ingest en cours en tuant le process rsync."""
    global _current_process
    if _current_process and _current_process.poll() is None:
        _current_process.terminate()
    STATE["cancelled"] = True


def reset_state():
    STATE.update({
        "status": "running",
        "running": True,
        "cancelled": False,
        "current_disk": None,
        "current_disk_index": 0,
        "total_disks": 0,
        "current_file": None,
        "speed": None,
        "eta": None,
        "disk_progress": 0,
        "total_progress": 0,
        "bytes_transferred": 0,
        "bytes_total": 0,
        "files_done": 0,
        "files_total": 0,
        "elapsed_seconds": 0,
        "logs": [],
        "last_report": None,
        "error": None,
    })


def count_files(path):
    count = 0
    for _, _, files in os.walk(path):
        count += len(files)
    return count


def rsync_copy_realtime(source_path, dest_path, disk_index, total_disks, global_start):
    """Lance rsync et parse la sortie en temps réel pour mettre à jour STATE."""
    global _current_process
    os.makedirs(dest_path, exist_ok=True)

    cmd = [
        "rsync",
        "-avh",
        "--info=progress2",
        "--no-inc-recursive",
        f"{source_path}/",
        f"{dest_path}/",
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    _current_process = process

    current_file = None

    for line in process.stdout:
        # Vérifier l'annulation à chaque ligne
        if STATE["cancelled"]:
            process.terminate()
            break

        line = line.rstrip()
        if not line:
            continue

        # Ligne de progression rsync
        m = _PROGRESS_RE.search(line)
        if m:
            pct = int(m.group(2))
            speed = m.group(3).replace(" ", "")
            eta = m.group(4)

            STATE["disk_progress"] = pct
            STATE["speed"] = speed
            STATE["eta"] = eta if eta != "--:--:--" else None
            STATE["elapsed_seconds"] = round(time.time() - global_start)

            # Progression globale : disques terminés + progression du disque en cours
            base = (disk_index / total_disks) * 100
            STATE["total_progress"] = round(base + (pct / total_disks))
            continue

        # Ligne de nom de fichier (pas une ligne de stats)
        m2 = _FILE_RE.match(line)
        if m2:
            current_file = os.path.basename(m2.group(1))
            STATE["current_file"] = current_file
            STATE["files_done"] += 1
            continue

        # Lignes ordinaires → log uniquement si intéressantes
        if line.startswith("sending") or line.startswith("created") or "error" in line.lower():
            log(f"  {line}")

    process.wait()
    STATE["disk_progress"] = 100
    return process.returncode == 0


def verify_copy(source_path, dest_path):
    missing = []
    mismatch = []

    for root, dirs, files in os.walk(source_path):
        for file in files:
            src_file = os.path.join(root, file)
            rel = os.path.relpath(src_file, source_path)
            dst_file = os.path.join(dest_path, rel)

            if not os.path.exists(dst_file):
                missing.append(rel)
            elif os.path.getsize(src_file) != os.path.getsize(dst_file):
                mismatch.append(rel)

    return missing, mismatch


def start_ingest(project_name=None):
    reset_state()
    global_start = time.time()

    try:
        sources = get_source_disks()
        master = get_master_disk()

        if not master:
            raise RuntimeError("Disque MASTER introuvable.")
        if not sources:
            raise RuntimeError("Aucun disque source détecté.")

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

        # Compter les fichiers totaux
        total_files = sum(count_files(d["path"]) for d in sources)
        STATE["files_total"] = total_files
        STATE["total_disks"] = len(sources)
        STATE["bytes_total"] = required_space

        log(f"Projet : {project_name}")
        log(f"Sources : {len(sources)} disque(s) — {format_bytes(required_space)} au total")
        log(f"Fichiers : {total_files}")

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

        for idx, disk in enumerate(sources):
            # Vérifier l'annulation entre chaque disque
            if STATE["cancelled"]:
                log("Ingest annulé par l'utilisateur.")
                break
            disk_name = disk["name"]
            STATE["current_disk"] = disk_name
            STATE["current_disk_index"] = idx + 1
            STATE["current_file"] = None
            STATE["disk_progress"] = 0
            STATE["files_done"] = 0

            disk_size = get_folder_size(disk["path"])
            log(f"[{idx+1}/{len(sources)}] {disk_name} — {format_bytes(disk_size)}")

            destination = os.path.join(rushes_root, disk_name)

            success = rsync_copy_realtime(
                disk["path"], destination, idx, len(sources), global_start
            )

            if not success:
                log(f"  Erreur rsync sur {disk_name}")

            missing, mismatch = verify_copy(disk["path"], destination)
            disk_success = success and not missing and not mismatch

            log(f"  Calcul checksums {disk_name}…")
            STATE["current_file"] = f"Calcul checksums {disk_name}…"
            destination_checksums = build_checksums(destination)

            report["sources"].append({
                "name": disk_name,
                "source_path": disk["path"],
                "destination_path": destination,
                "size_bytes": disk_size,
                "size_human": format_bytes(disk_size),
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

        STATE["total_progress"] = 98
        STATE["current_file"] = "Écriture des rapports…"
        STATE["speed"] = None
        STATE["eta"] = None

        # Si annulé, on saute les rapports
        if STATE["cancelled"]:
            STATE["status"] = "cancelled"
            log("Ingest annulé — aucun rapport généré.")
            return

        elapsed = round(time.time() - global_start, 2)
        report["finished_at"] = datetime.now().isoformat()
        report["duration_seconds"] = elapsed
        report["success"] = all(s["success"] for s in report["sources"])

        json_report_path = os.path.join(reports_root, "ingest_report.json")
        txt_report_path = os.path.join(reports_root, "ingest_report.txt")
        checksums_path = os.path.join(reports_root, "checksums.sha256")

        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        with open(txt_report_path, "w", encoding="utf-8") as f:
            f.write(f"Projet : {project_name}\n")
            f.write(f"Succès : {report['success']}\n")
            f.write(f"Durée  : {_fmt_duration(elapsed)}\n")
            f.write(f"Volume : {format_bytes(required_space)}\n\n")
            for source in report["sources"]:
                f.write(f"{source['name']} : {'OK' if source['success'] else 'ERREUR'}\n")
                if source["missing_files"]:
                    f.write(f"  Manquants : {source['missing_files']}\n")
                if source["checksum_mismatch"]:
                    f.write(f"  Checksums incorrects : {source['checksum_mismatch']}\n")

        write_checksum_file(all_checksums, checksums_path)

        STATE["last_report"] = report
        STATE["total_progress"] = 100
        STATE["current_file"] = None
        STATE["status"] = "complete" if report["success"] else "complete_with_errors"
        log(f"Ingest terminé en {_fmt_duration(elapsed)}.")

    except Exception as e:
        STATE["error"] = str(e)
        STATE["status"] = "error"
        log(f"ERREUR FATALE : {e}")

    finally:
        STATE["running"] = False
        STATE["current_disk"] = None
        STATE["elapsed_seconds"] = round(time.time() - global_start)


def _fmt_duration(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    if m > 0:
        return f"{m}m {s:02d}s"
    return f"{s}s"
