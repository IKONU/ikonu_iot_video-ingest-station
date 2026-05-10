#!/bin/bash
# ============================================================
#  IKONU IoT Video Ingest Station — Désinstallation
# ============================================================
set -e

APP_DIR="$HOME/ikonu_iot_video-ingest-station"

echo ""
echo "========================================"
echo "  IKONU Ingest Station — Désinstallation"
echo "========================================"
echo ""

read -p "Confirmer la désinstallation ? (oui/non) : " CONFIRM
if [ "$CONFIRM" != "oui" ]; then
  echo "Annulé."
  exit 0
fi

echo "[1/3] Arrêt et suppression du service systemd..."
sudo systemctl stop ingest-station.service 2>/dev/null || true
sudo systemctl disable ingest-station.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/ingest-station.service
sudo systemctl daemon-reload

echo "[2/3] Suppression du mode kiosk..."
rm -f "$HOME/.config/autostart/ingest-browser.desktop"

echo "[3/3] Suppression de l'environnement virtuel Python..."
rm -rf "$APP_DIR/venv"

echo ""
echo "Désinstallation terminée."
echo "Le code source dans $APP_DIR n'a pas été supprimé."
echo "Pour tout supprimer : rm -rf $APP_DIR"
echo ""
