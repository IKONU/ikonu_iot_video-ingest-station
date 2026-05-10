# Dépannage — IKONU Ingest Station

---

## Le MASTER n'est pas détecté

**Cause probable :** Le SSD n'est pas nommé exactement `MASTER` (sensible à la casse).

**Solution :**
- Sur macOS : Finder → clic droit → Lire les informations → renommer
- Sur Windows : Explorateur → clic droit → Renommer
- Sur Linux :
  ```bash
  sudo mlabel -i /dev/sdX1 ::MASTER   # exFAT
  ```

---

## Les SSD caméra ne sont pas détectés

**Cause probable 1 :** Le hub USB n'est pas alimenté → manque de puissance.

**Solution :** Utiliser un hub USB alimenté (avec son propre adaptateur secteur).

**Cause probable 2 :** Format non reconnu.

**Solution :** Vérifier que les disques sont en exFAT ou FAT32.

---

## Erreur de copie rsync

**Symptôme :** `ERREUR : CAM_A` dans le journal.

**Causes possibles :**
1. Câble USB défaillant → changer de câble
2. Hub surchargé → brancher un disque à la fois pour tester
3. Disque source en lecture seule → vérifier les permissions

**Vérifier les logs système :**
```bash
sudo journalctl -u ingest-station.service -f
```

---

## L'interface ne répond pas

**Vérifier que le service tourne :**
```bash
sudo systemctl status ingest-station.service
```

**Redémarrer le service :**
```bash
sudo systemctl restart ingest-station.service
```

**Voir les erreurs Python :**
```bash
sudo journalctl -u ingest-station.service --no-pager -n 50
```

---

## Le mode kiosk ne démarre pas

**Vérifier le fichier autostart :**
```bash
cat ~/.config/autostart/ingest-browser.desktop
```

**Vérifier que Chromium est installé :**
```bash
which chromium-browser
```

**Réinstaller si besoin :**
```bash
sudo apt install chromium-browser
```

---

## L'ingest est très lent

**Cause normale :** Les checksums SHA256 sur de gros fichiers prennent du temps.

**Estimation :** Environ 100–150 Mo/s en lecture sur USB 3.

Pour 1 To de données : prévoir 2–3 heures (copie + checksum).

---

## Espace insuffisant affiché alors que MASTER est grand

**Cause :** Le disque est monté en lecture seule ou le système de fichiers est corrompu.

**Solution :**
```bash
# Vérifier le montage
mount | grep MASTER

# Vérifier les droits
ls -la /media/pi/MASTER
```

---

## Réinitialiser complètement

```bash
cd ~/ikonu_iot_video-ingest-station
./scripts/uninstall.sh
./scripts/install.sh
```

---

## Contacter le support

Ouvrir une issue sur le dépôt GitHub :
https://github.com/TON-USER/ikonu_iot_video-ingest-station/issues
