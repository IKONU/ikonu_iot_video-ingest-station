# IKONU IoT Video Ingest Station

Station d'ingest vidéo autonome pour Raspberry Pi 4B.

---

## Fonctionnalités

- Détection automatique des SSD caméra branchés via hub USB
- Exclusion automatique du disque MASTER des sources
- Calcul et vérification de l'espace disponible
- Copie propre via `rsync` avec vérification de checksum
- Génération de checksums SHA256 post-copie
- Rapport d'ingest au format JSON et TXT
- Interface web tactile locale
- Démarrage automatique en mode kiosk sur écran tactile
- Service systemd (relance automatique)
- Installation entièrement automatisée depuis GitHub

---

## Matériel recommandé

| Matériel | Modèle |
|---|---|
| Raspberry Pi | 4B — 4 Go RAM |
| Écran tactile | Waveshare 4.3" DSI |
| Hub USB | UGREEN 4 ports 10 Gbps |
| SSD MASTER | Crucial X10 Pro ou équivalent |
| SSD caméra | Samsung T7 / T9 ou équivalent |

---

## Installation rapide

```bash
# Sur le Raspberry Pi :
git clone https://github.com/TON-USER/ikonu_iot_video-ingest-station.git ~/ikonu_iot_video-ingest-station
cd ~/ikonu_iot_video-ingest-station
chmod +x scripts/*.sh
./scripts/install.sh
sudo reboot
```

---

## Mise à jour

```bash
cd ~/ikonu_iot_video-ingest-station
./scripts/update.sh
```

---

## Accès à l'interface

- Écran tactile : démarre automatiquement au boot
- Réseau local : `http://ingest-station.local:8080`

---

## Structure des dossiers sur le MASTER

```
MASTER/
└── 2026-08-08 - NOM_TOURNAGE/
    ├── 01_RUSHES/
    │   ├── CAM_A/
    │   ├── CAM_B/
    │   └── CAM_D/
    ├── 02_AUDIO/
    ├── 03_PROXIES/
    ├── 04_PROJECT/
    ├── 05_EXPORTS/
    └── 99_REPORTS/
        ├── ingest_report.json
        ├── ingest_report.txt
        └── checksums.sha256
```

---

## Nommage des disques

| Disque | Nom obligatoire |
|---|---|
| Disque de destination | `MASTER` |
| Caméra A | `CAM_A` |
| Caméra B | `CAM_B` |
| Caméra C | `CAM_C` |
| Caméra D | `CAM_D` |
| Audio | `AUDIO_A` |
| Drone | `DRONE_A` |

---

## Documentation

- [Installation complète](docs/INSTALL.md)
- [Guide d'utilisation](docs/USAGE.md)
- [Dépannage](docs/TROUBLESHOOTING.md)
- [Créer une image SD de sauvegarde](scripts/create_image_notes.md)

---

## Structure du dépôt

```
ikonu_iot_video-ingest-station/
├── app/
│   ├── app.py
│   ├── config.py
│   ├── ingest.py
│   ├── disk_utils.py
│   ├── checksum.py
│   └── templates/
│       └── index.html
├── scripts/
│   ├── install.sh
│   ├── update.sh
│   ├── uninstall.sh
│   └── create_image_notes.md
├── systemd/
│   └── ingest-station.service
├── kiosk/
│   └── ingest-browser.desktop
└── docs/
    ├── INSTALL.md
    ├── USAGE.md
    └── TROUBLESHOOTING.md
```

---

## Licence

MIT — voir [LICENSE](LICENSE)
