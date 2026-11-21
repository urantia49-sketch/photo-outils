# photo-outils

Outils pour organiser et vérifier la photothèque (Synology Drive Photos).

## Prérequis

- Python 3
- [exiftool](https://exiftool.org/) (`brew install exiftool`)

## Outils

### `outils/check_photo_dates.py`

Vérifie la cohérence entre le nom des dossiers photos (format `AAAA-MM-JJ`) et
la date de prise de vue réelle (EXIF) des fichiers qu'ils contiennent. Gère
JPG, RAW (CR2, CR3, NEF, ARW, DNG, ...), TIFF, HEIC et vidéos (MOV, MP4).

```bash
python3 outils/check_photo_dates.py <dossier_racine> [--tolerance N] [--csv sortie.csv]
```

- `<dossier_racine>` : dossier contenant les sous-dossiers datés (ex: le dossier d'une année)
- `--tolerance N` : écart en jours toléré avant de signaler une incohérence (défaut: 0)
- `--csv sortie.csv` : exporte le détail des fichiers en incohérence. Les chemins relatifs sont
  écrits dans `resultats/` (créé automatiquement) ; utilisez un chemin absolu pour écrire ailleurs.

À chaque exécution, une synthèse de l'analyse (identique à la sortie console) est aussi écrite
dans `logs/<dossier_racine>_<horodatage>.log` (créé automatiquement).

Exemple :

```bash
python3 outils/check_photo_dates.py \
  "/Users/remi/Library/CloudStorage/SynologyDrive-Photos/2026"
```
