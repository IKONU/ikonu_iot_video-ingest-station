# Guide d'utilisation — IKONU Ingest Station

## Avant le tournage

- Formater les SSD caméra et les nommer exactement :
  - `CAM_A`, `CAM_B`, `CAM_C`, `CAM_D`
  - `AUDIO_A`, `DRONE_A` (selon besoins)
- Vérifier que le SSD MASTER est nommé **MASTER**
- Formater en **exFAT** (compatible Mac, Windows, Linux)

---

## Workflow d'ingest

### 1. Brancher les disques

Brancher sur le hub USB :
- SSD MASTER
- SSD caméra (autant que nécessaire)

Attendre 5–10 secondes que le Raspberry Pi les détecte.

### 2. Accéder à l'interface

L'interface s'ouvre automatiquement sur l'écran tactile.

Depuis un autre appareil sur le même réseau :
```
http://ingest-station.local:8080
```

### 3. Vérifier l'affichage

L'interface doit afficher :
- ✅ MASTER détecté avec l'espace disponible
- ✅ Les disques source (CAM_A, etc.) avec l'espace utilisé
- ✅ Espace requis vs disponible

### 4. Saisir le nom du projet

Format recommandé :
```
2026-08-08 - NOM_DU_TOURNAGE
```

### 5. Lancer l'ingest

Appuyer sur **▶ START INGEST**.

Suivre la progression dans le journal en temps réel.

---

## Structure créée sur le MASTER

```
MASTER/
└── 2026-08-08 - NOM_DU_TOURNAGE/
    ├── 01_RUSHES/
    │   ├── CAM_A/
    │   ├── CAM_B/
    │   ├── CAM_C/
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

## Après l'ingest

### Vérifier le rapport

```bash
cat /media/pi/MASTER/NOM_PROJET/99_REPORTS/ingest_report.txt
```

Ou directement sur l'écran tactile dans le journal.

### Si tout est OK

- Le MASTER est prêt pour le montage
- Les SSD caméra peuvent être archivés ou reformatés **après validation**

---

## Mise à jour du système

```bash
cd ~/ikonu_iot_video-ingest-station
./scripts/update.sh
```

---

## Variables d'environnement disponibles

| Variable | Défaut | Description |
|---|---|---|
| `INGEST_MOUNT_BASE` | `/media/pi` | Dossier de montage des disques |
| `INGEST_MASTER_NAME` | `MASTER` | Nom du disque maître |
| `INGEST_PORT` | `8080` | Port de l'interface web |

Pour modifier, éditer `/etc/systemd/system/ingest-station.service` puis :

```bash
sudo systemctl daemon-reload
sudo systemctl restart ingest-station.service
```
