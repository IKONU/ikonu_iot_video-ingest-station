from flask import Flask, jsonify, request, render_template
import threading

from config import HOST, PORT, APP_NAME, MASTER_VOLUME_NAME
from disk_utils import get_mounted_disks, get_source_disks, get_master_disk, get_folder_size, format_bytes
from ingest import STATE, start_ingest

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", app_name=APP_NAME)


@app.route("/api/disks")
def api_disks():
    disks = get_mounted_disks()
    sources = get_source_disks()
    master = get_master_disk()

    required_space = sum(get_folder_size(disk["path"]) for disk in sources)

    return jsonify({
        "master_name": MASTER_VOLUME_NAME,
        "disks": disks,
        "sources": sources,
        "master": master,
        "required_space_bytes": required_space,
        "required_space_human": format_bytes(required_space),
        "can_start": bool(master and sources and master["free"] >= required_space),
    })


@app.route("/api/state")
def api_state():
    return jsonify(STATE)


@app.route("/api/start", methods=["POST"])
def api_start():
    data = request.get_json(silent=True) or {}
    project_name = data.get("project_name")

    if STATE["running"]:
        return jsonify({"ok": False, "error": "Ingest déjà en cours"}), 409

    thread = threading.Thread(target=start_ingest, args=(project_name,))
    thread.daemon = True
    thread.start()

    return jsonify({"ok": True})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    if STATE["running"]:
        return jsonify({"ok": False, "error": "Ingest en cours, impossible de réinitialiser"}), 409
    STATE["status"] = "idle"
    STATE["logs"] = []
    STATE["last_report"] = None
    STATE["error"] = None
    STATE["progress"] = 0
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
