---
name: stats-phototheque
description: Statistiques de la photothèque Synology — fichiers et volume par année et par type, appareils utilisés, dossiers vides ou mal nommés. À utiliser quand l'utilisateur demande combien de photos il a, la taille de sa photothèque, quels appareils, ou un état des lieux.
---

# Statistiques de la photothèque

Script : `outils/stats_phototheque.py` (depuis la racine de photo-outils)

1. Périmètre : toute la photothèque
   (`/Users/remi/Library/CloudStorage/SynologyDrive-Photos`) par défaut, ou une année.
2. Lancer :
   ```bash
   python3 outils/stats_phototheque.py "<dossier>" [--exif]
   ```
   `--exif` ajoute la répartition par appareil mais lit les métadonnées de chaque fichier :
   le proposer pour une année, ou en arrière-plan pour toute la photothèque.
3. Restituer en français :
   - tableau par année (dossiers, fichiers, volume) et total ;
   - répartition par type (JPG / RAW / vidéo...) et par appareil si demandé ;
   - points d'attention : dossiers sans média, dossiers sans date `AAAA-MM-JJ`, fichiers
     non médias inattendus ;
   - observations utiles (année anormalement vide, part des RAW, vidéos lourdes...).
4. Suggérer les suites : `/corriger-dossiers-photos`, `/doublons-photos`, ou ranger les
   dossiers mal nommés. Lecture seule : ne rien modifier.
