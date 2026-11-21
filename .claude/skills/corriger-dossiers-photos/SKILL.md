---
name: corriger-dossiers-photos
description: Renomme les dossiers photos AAAA-MM-JJ dont la date ne correspond pas à la date EXIF majoritaire, avec simulation obligatoire puis confirmation. À utiliser quand l'utilisateur veut corriger, réparer ou renommer des dossiers photos mal datés, typiquement après /verifier-dates-photos.
---

# Corriger les dossiers photos mal datés

Racine : `/Users/remi/Library/CloudStorage/SynologyDrive-Photos/<année>`
Script : `outils/corriger_dossiers.py` (depuis la racine de photo-outils)

1. Déterminer l'année (argument ou demander) et vérifier que le dossier existe.
2. **Simulation d'abord** (obligatoire) :
   ```bash
   python3 outils/corriger_dossiers.py "<racine>/<année>" --csv plan_<année>.csv [--seuil 0.8]
   ```
   Le suffixe du nom (ex. ` Ski`) est conservé ; seule la date en tête change.
3. Présenter le plan en tableau : ancien nom → nouveau nom, part des fichiers, statut.
   Expliquer les lignes « ignoré » (majorité sous le seuil : le dossier mélange plusieurs
   jours, souvent un appareil mal réglé ou un dossier fourre-tout) et « conflit ».
4. **Demander une confirmation explicite** avant d'appliquer. L'utilisateur peut exclure
   certains dossiers : dans ce cas, renommer ceux-là à la main avec `mv` un par un plutôt que
   lancer `--appliquer` sur toute l'année.
5. Après accord :
   ```bash
   python3 outils/corriger_dossiers.py "<racine>/<année>" --appliquer --csv applique_<année>.csv
   ```
6. Rappeler que Synology Drive va synchroniser les renommages, et relancer
   `/verifier-dates-photos` sur l'année pour confirmer.
