# Guide d'installation complet — IKONU Ingest Station

> **Document de référence** — À imprimer ou garder ouvert pendant l'installation.
> Temps total estimé : **30 à 45 minutes**.

---

## Matériel nécessaire

| Matériel | Modèle / Détail |
|---|---|
| Raspberry Pi 4B | 4 Go RAM recommandé |
| Carte SD | 16 Go minimum — Classe 10 / A2 |
| Écran tactile | Waveshare 4.3" DSI |
| Hub USB-C | UGREEN 4 ports 10 Gbps |
| SSD MASTER | Crucial X10 Pro — **nommé MASTER** |
| SSD caméra | Samsung T7/T9 — **nommés CAM_A, CAM_B…** |
| Câble HDMI | Pour le premier démarrage si pas d'écran DSI |
| Câble Ethernet | Recommandé pour l'installation |

---

## PHASE 1 — Préparer la carte SD

### 1.1 — Télécharger Raspberry Pi Imager

→ https://www.raspberrypi.com/software/

Disponible sur macOS, Windows, Linux.

### 1.2 — Flasher la carte SD

Dans Raspberry Pi Imager :

1. **Choisir le modèle** : Raspberry Pi 4
2. **Choisir l'OS** : `Raspberry Pi OS (64-bit)` — version **Desktop**
3. **Choisir le stockage** : ta carte SD

### 1.3 — Configurer avant de flasher

Cliquer sur l'icône ⚙️ **"Modifier les réglages"** et renseigner :

| Paramètre | Valeur |
|---|---|
| Hostname | `ingest-station` |
| Utilisateur | `pi` (ou ton prénom) |
| Mot de passe | Ton choix |
| Wi-Fi SSID | Ton réseau |
| Wi-Fi mot de passe | Ton mot de passe |
| Wi-Fi pays | FR |
| SSH activé | ✅ Oui |
| Timezone | `Europe/Paris` |
| Clavier | `fr` |

Cliquer **Sauvegarder** puis **Écrire**.

### 1.4 — Insérer et démarrer

Insérer la carte SD dans le Raspberry Pi et brancher l'alimentation.

Attendre 1–2 minutes le premier démarrage complet.

---

## PHASE 2 — Première connexion et mise à jour système

### 2.1 — Se connecter

**Option A — Via SSH depuis ton ordinateur :**
```bash
ssh pi@ingest-station.local
```

**Option B — Directement sur le Raspberry** avec clavier + écran.

### 2.2 — Mise à jour complète du système

**Étape critique — à ne pas sauter.**

Les drivers USB, le kernel et la gestion des SSD ont beaucoup évolué.
Une mise à jour garantit stabilité et compatibilité des disques.

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Attendre le redémarrage puis se reconnecter.

### 2.3 — Installer le support des systèmes de fichiers

Pour que les SSD en **exFAT** (caméras) et **NTFS** soient bien montés :

```bash
sudo apt install -y exfat-fuse exfatprogs ntfs-3g
```

### 2.4 — Vérifier la détection des disques USB

Brancher un SSD et vérifier qu'il apparaît :

```bash
lsblk
```

Tu dois voir quelque chose comme :
```
sda           8:0    1 931.5G  0 disk
└─sda1        8:1    1 931.5G  0 part  /media/pi/MASTER
```

Si le disque est absent → vérifier le hub / le câble.

---

## PHASE 3 — Installer le projet IKONU

### 3.1 — Cloner le dépôt GitHub

```bash
git clone https://github.com/TON-USER/ikonu_iot_video-ingest-station.git ~/ikonu_iot_video-ingest-station
cd ~/ikonu_iot_video-ingest-station
```

> Remplacer `TON-USER` par ton nom d'utilisateur GitHub.

### 3.2 — Lancer l'installation automatique

```bash
chmod +x scripts/*.sh
./scripts/install.sh
```

Le script installe automatiquement :

- ✅ Python 3 + environnement virtuel
- ✅ Flask (serveur web)
- ✅ rsync (copie des fichiers)
- ✅ Chromium (navigateur kiosk)
- ✅ Service systemd (démarrage automatique)
- ✅ Mode kiosk sur l'écran tactile

### 3.3 — Note si ton utilisateur n'est pas `pi`

Avant de lancer `install.sh`, éditer le fichier service :

```bash
nano ~/ikonu_iot_video-ingest-station/systemd/ingest-station.service
```

Remplacer les 3 occurrences de `/home/pi/` par `/home/TON_NOM/`
et `User=pi` par `User=TON_NOM`.

Sauvegarder : `Ctrl+O` → `Entrée` → `Ctrl+X`

---

## PHASE 4 — Redémarrage final

```bash
sudo reboot
```

Après le redémarrage :

- Chromium s'ouvre automatiquement en mode kiosk
- L'interface IKONU s'affiche sur l'écran tactile
- Le service tourne en arrière-plan

---

## PHASE 5 — Vérifications post-installation

### 5.1 — Vérifier le service

```bash
sudo systemctl status ingest-station.service
```

Résultat attendu : `active (running)`

### 5.2 — Tester l'interface web

Depuis un autre appareil sur le même réseau :
```
http://ingest-station.local:8080
```

### 5.3 — Tester un ingest complet

1. Brancher un SSD nommé `CAM_A` avec quelques fichiers test
2. Brancher le SSD `MASTER`
3. Attendre la détection (5–10 secondes)
4. Saisir un nom de projet dans l'interface
5. Appuyer sur **▶ START INGEST**
6. Vérifier le rapport dans `99_REPORTS/`

---

## PHASE 6 — Sauvegarde de la carte SD

Une fois tout validé, créer une image de sauvegarde.

**Éteindre le Raspberry Pi :**
```bash
sudo poweroff
```

Retirer la carte SD et la connecter à ton ordinateur.

**Sur macOS :**
```bash
# Identifier le disque (ex: disk4)
diskutil list

# Créer l'image (remplacer diskX)
sudo dd if=/dev/rdiskX of=~/ikonu-ingest-station-backup-2026.img bs=4m status=progress

# Compresser
gzip -9 ~/ikonu-ingest-station-backup-2026.img
```

**Sur Linux :**
```bash
lsblk
sudo dd if=/dev/sdX of=~/ikonu-ingest-station-backup-2026.img bs=4M status=progress
gzip -9 ~/ikonu-ingest-station-backup-2026.img
```

> Cette image permet de restaurer le système complet en quelques minutes.
> Stocker une copie sur le disque MASTER dans un dossier `_SYSTEM_BACKUPS`.

---

## Commandes utiles au quotidien

```bash
# Voir les logs en direct
sudo journalctl -u ingest-station.service -f

# Redémarrer le service
sudo systemctl restart ingest-station.service

# Mettre à jour le projet
cd ~/ikonu_iot_video-ingest-station
./scripts/update.sh

# Voir les disques connectés
lsblk

# Voir l'espace disque
df -h
```

---

## Résumé des étapes en une page

```
[ 1 ] Flash carte SD avec Raspberry Pi Imager (OS Desktop 64-bit)
        → hostname: ingest-station | user: pi | SSH: oui

[ 2 ] Premier démarrage + mise à jour système
        sudo apt update && sudo apt full-upgrade -y && sudo reboot

[ 3 ] Installer support exFAT/NTFS
        sudo apt install -y exfat-fuse exfatprogs ntfs-3g

[ 4 ] Tester détection USB
        lsblk

[ 5 ] Cloner le projet
        git clone https://github.com/TON-USER/ikonu_iot_video-ingest-station.git ~/ikonu_iot_video-ingest-station

[ 6 ] Installer
        cd ~/ikonu_iot_video-ingest-station
        chmod +x scripts/*.sh
        ./scripts/install.sh

[ 7 ] Redémarrer
        sudo reboot

[ 8 ] Vérifier
        sudo systemctl status ingest-station.service
        → http://ingest-station.local:8080

[ 9 ] Sauvegarder la carte SD (image .img)
```

---

## En cas de problème

Consulter [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
