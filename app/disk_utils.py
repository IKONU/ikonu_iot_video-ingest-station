import os
import shutil
from config import MOUNT_BASE, MASTER_VOLUME_NAME, EXCLUDED_NAMES


def get_mounted_disks():
    if not os.path.exists(MOUNT_BASE):
        return []

    disks = []

    for name in sorted(os.listdir(MOUNT_BASE)):
        path = os.path.join(MOUNT_BASE, name)

        if not os.path.ismount(path):
            continue

        usage = shutil.disk_usage(path)

        disks.append({
            "name": name,
            "path": path,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "is_master": name == MASTER_VOLUME_NAME
        })

    return disks


def get_source_disks():
    return [
        disk for disk in get_mounted_disks()
        if disk["name"] not in EXCLUDED_NAMES
        and not disk["is_master"]
    ]


def get_master_disk():
    for disk in get_mounted_disks():
        if disk["name"] == MASTER_VOLUME_NAME:
            return disk
    return None


def get_folder_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total += os.path.getsize(file_path)
            except OSError:
                pass
    return total


def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"
