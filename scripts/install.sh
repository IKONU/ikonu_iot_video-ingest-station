#!/bin/bash
# ============================================================
#  IKONU IoT Video Ingest Station — Installation
# ============================================================
set -e

APP_DIR="$HOME/ikonu_iot_video-ingest-station"
SERVICE_NAME="ingest-station.service"
VENV_DIR="$APP_DIR/venv"

echo ""
echo "========================================"
echo "  IKONU Ingest Station — Installation"
echo "========================================"
echo ""

# --- Vérification du répertoire ---
if [ ! -d "$APP_DIR" ]; then
  echo "ERREUR : Le répertoire $APP_DIR est introuvable."
  echo "Lance d'abord : git clone https://github.com/TON-USER/ikonu_iot_video-ingest-station.git ~/ikonu_iot_video-ingest-station"
  exit 1
fi

# --- Dépendances système ---
echo "[1/5] Installation des dépendances système..."
sudo apt-get update -q

# Chromium : nom du paquet différent selon la version de l'OS
if apt-cache show chromium &>/dev/null; then
  CHROMIUM_PKG="chromium"
else
  CHROMIUM_PKG="chromium-browser"
fi

# exFAT : exfatprogs remplace exfat-utils sur Bookworm/Trixie
if apt-cache show exfatprogs &>/dev/null; then
  EXFAT_PKG="exfatprogs"
else
  EXFAT_PKG="exfat-utils"
fi

sudo apt-get install -y python3 python3-pip python3-venv rsync git \
  "$CHROMIUM_PKG" exfat-fuse "$EXFAT_PKG" ntfs-3g

# --- Environnement virtuel Python ---
echo "[2/5] Création de l'environnement Python..."
cd "$APP_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet
pip install flask psutil --quiet
deactivate

# --- Service systemd ---
echo "[3/5] Installation du service systemd..."
sudo cp "$APP_DIR/systemd/$SERVICE_NAME" /etc/systemd/system/$SERVICE_NAME
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

# --- Mode kiosk (démarrage automatique de Chromium) ---
echo "[4/5] Configuration du mode kiosk..."
mkdir -p "$HOME/.config/autostart"
cp "$APP_DIR/kiosk/ingest-browser.desktop" "$HOME/.config/autostart/ingest-browser.desktop"

# --- Droits de montage USB ---
echo "[5/5] Configuration des droits de montage..."
sudo usermod -aG plugdev "$USER" 2>/dev/null || true

echo ""
echo "========================================"
echo "  Installation terminée !"
echo "========================================"
echo ""
echo "  Interface web : http://localhost:8080"
echo "  Réseau local  : http://$(hostname).local:8080"
echo ""
echo "  Redémarre le Raspberry Pi pour activer le mode kiosk :"
echo "  sudo reboot"
echo ""
