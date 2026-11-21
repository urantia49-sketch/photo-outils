---
name: verifier-dates-photos
description: Lance check_photo_dates.py sur un dossier d'année de la photothèque Synology et résume les incohérences entre nom de dossier (AAAA-MM-JJ) et date EXIF. À utiliser quand l'utilisateur veut vérifier, contrôler ou auditer les dates de ses photos ou d'une année.
---

# Vérifier les dates des photos

Racine de la photothèque : `/Users/remi/Library/CloudStorage/SynologyDrive-Photos/`

1. Déterminer l'année (argument, ou demander ; par défaut l'année en cours).
   Vérifier que `<racine>/<année>` existe et que `exiftool` est installé (`command -v exiftool`).
2. Depuis la racine du projet `photo-outils` :
   ```bash
   python3 outils/check_photo_dates.py "<racine>/<année>" --csv incoherences_<année>.csv [--tolerance N]
   ```
   Le dossier peut être volumineux (fichiers synchronisés à la demande) : lancer avec un
   timeout long ou en arrière-plan.
3. Résumer en français : nb de dossiers/fichiers analysés, dossiers en incohérence (les pires
   en premier, avec l'écart en jours), fichiers sans date EXIF. Indiquer les chemins du log
   (`logs/`) et du CSV (`resultats/`).
4. Proposer des pistes (renommer le dossier, appareil mal réglé, ...) mais **ne jamais
   renommer ni déplacer de fichiers** de la photothèque sans demande explicite.
