# Notes — Création d'une image SD de sauvegarde

## Quand créer une image ?

Après que le système est parfaitement installé et testé, créer une image SD
permet de cloner la station sur un autre Raspberry Pi ou de la restaurer
rapidement en cas de panne.

---

## Méthode 1 — Depuis macOS / Linux

### Identifier le disque SD

```bash
diskutil list          # macOS
lsblk                  # Linux
```

### Créer l'image (remplacer /dev/diskX par le bon disque)

**macOS :**
```bash
sudo dd if=/dev/rdiskX of=~/ikonu-ingest-station-backup.img bs=4m status=progress
```

**Linux :**
```bash
sudo dd if=/dev/sdX of=~/ikonu-ingest-station-backup.img bs=4M status=progress
```

### Compresser l'image

```bash
gzip -9 ikonu-ingest-station-backup.img
# Résultat : ikonu-ingest-station-backup.img.gz
```

---

## Méthode 2 — Avec Raspberry Pi Imager (GUI)

1. Ouvrir **Raspberry Pi Imager**
2. Choisir *Use custom image* → sélectionner le `.img`
3. Choisir la carte SD cible
4. Cliquer *Write*

---

## Méthode 3 — Depuis le Raspberry Pi lui-même (sur disque externe)

```bash
sudo apt install rpi-clone
sudo rpi-clone sdX       # remplacer sdX par la carte cible
```

---

## Restaurer une image

```bash
# macOS
sudo dd if=ikonu-ingest-station-backup.img of=/dev/rdiskX bs=4m

# Linux
sudo dd if=ikonu-ingest-station-backup.img of=/dev/sdX bs=4M status=progress
```

---

## Recommandation

- Nommer les images avec la date : `ikonu-ingest-2026-08-08.img.gz`
- Stocker sur le disque MASTER dans un dossier `_SYSTEM_BACKUPS`
- Conserver au minimum 2 copies sur des supports différents
