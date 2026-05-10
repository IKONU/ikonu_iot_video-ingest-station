#!/bin/bash
# ============================================================
#  IKONU IoT Video Ingest Station — Mise à jour
# ============================================================
set -e

APP_DIR="$HOME/ikonu_iot_video-ingest-station"

echo ""
echo "========================================"
echo "  IKONU Ingest Station — Mise à jour"
echo "========================================"
echo ""

if [ ! -d "$APP_DIR" ]; then
  echo "ERREUR : $APP_DIR introuvable. Lance d'abord install.sh."
  exit 1
fi

cd "$APP_DIR"

echo "[1/3] Récupération des dernières modifications GitHub..."
git pull

echo "[2/3] Mise à jour des dépendances Python..."
source venv/bin/activate
pip install --upgrade flask psutil --quiet
deactivate

echo "[3/3] Redémarrage du service..."
sudo systemctl restart ingest-station.service

echo ""
echo "Mise à jour terminée. Service redémarré."
echo ""
