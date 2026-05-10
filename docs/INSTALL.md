# Guide d'installation — IKONU Ingest Station

## Prérequis matériels

| Matériel | Détail |
|---|---|
| Raspberry Pi 4B | 4 Go RAM recommandé |
| Écran tactile Waveshare 4.3" DSI | Connecté sur port DSI |
| Hub USB-C 4 ports | UGREEN 10 Gbps |
| SSD MASTER | Ex : Crucial X10 — nommé **MASTER** |
| SSD caméra | Nommés **CAM_A**, **CAM_B**, **CAM_C**, **CAM_D** |

---

## Étape 1 — Préparer la carte SD

1. Télécharger **Raspberry Pi Imager** : https://www.raspberrypi.com/software/
2. Flasher **Raspberry Pi OS Lite (64-bit)** ou la version Desktop
3. Dans les options avancées de l'Imager :
   - Activer SSH
   - Définir le nom d'hôte : `ingest-station`
   - Créer un utilisateur : `pi` (ou ton prénom)
   - Configurer le Wi-Fi si besoin
4. Insérer la carte SD dans le Raspberry Pi et démarrer

---

## Étape 2 — Connexion initiale

```bash
# Depuis ton ordinateur (SSH)
ssh pi@ingest-station.local

# Ou directement sur le Raspberry avec clavier/écran
```

---

## Étape 3 — Cloner le dépôt

```bash
git clone https://github.com/TON-USER/ikonu_iot_video-ingest-station.git ~/ikonu_iot_video-ingest-station
cd ~/ikonu_iot_video-ingest-station
```

---

## Étape 4 — Lancer l'installation

```bash
chmod +x scripts/*.sh
./scripts/install.sh
```

Le script installe automatiquement :
- Python 3 + Flask
- rsync
- Chromium
- Le service systemd
- Le mode kiosk au démarrage

---

## Étape 5 — Redémarrer

```bash
sudo reboot
```

Après le redémarrage, Chromium s'ouvre automatiquement sur l'interface d'ingest.

---

## Étape 6 — Vérifier le service

```bash
sudo systemctl status ingest-station.service
```

---

## Accès depuis un autre appareil

```
http://ingest-station.local:8080
```

---

## Note : si ton utilisateur n'est pas `pi`

Éditer le fichier `systemd/ingest-station.service` avant d'installer :

```ini
User=TON_NOM
WorkingDirectory=/home/TON_NOM/ikonu_iot_video-ingest-station/app
ExecStart=/home/TON_NOM/ikonu_iot_video-ingest-station/venv/bin/python ...
```

Puis relancer :
```bash
./scripts/install.sh
```
