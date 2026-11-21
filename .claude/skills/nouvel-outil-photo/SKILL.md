---
name: nouvel-outil-photo
description: Crée un nouveau script dans photo-outils/outils/ en respectant les conventions du projet (argparse, logs, CSV, simulation par défaut, README). À utiliser quand l'utilisateur veut un nouvel outil, script ou fonctionnalité pour sa photothèque.
---

# Nouvel outil photo

1. Clarifier le besoin : entrée (dossier d'année ? photothèque entière ?), sortie attendue,
   et surtout **l'outil modifie-t-il des fichiers ?**
2. Partir d'un outil existant comme modèle : `outils/corriger_dossiers.py` (s'il modifie des
   fichiers) ou `outils/check_photo_dates.py` (lecture seule). Conventions obligatoires :
   - Python 3.9 compatible (pas de `X | Y` dans les annotations, pas de `match`),
     bibliothèque standard uniquement ;
   - nom de fichier en français, `snake_case` ; docstring d'usage avec exemple en tête ;
   - `argparse` avec aides en français ;
   - métadonnées via `exiftool -j` en sous-processus, message clair si exiftool est absent ;
   - constantes `RESULTATS_DIR` / `LOGS_DIR` relatives à la racine du projet ;
   - fonction `log()` qui affiche ET collecte, synthèse écrite dans
     `logs/<outil>_<dossier>_<horodatage>.log` ;
   - `--csv` optionnel, chemins relatifs dans `resultats/` ;
   - **si l'outil modifie, renomme, déplace ou supprime** : simulation par défaut, option
     `--appliquer` explicite, jamais de suppression directe.
3. Tester sur une fausse photothèque dans le dossier temporaire (scratchpad) : créer
   quelques JPEG (`sips -s format jpeg` à partir d'un PNG), poser des dates avec
   `exiftool -overwrite_original -DateTimeOriginal=...`. Ne jamais tester sur la vraie
   photothèque. Supprimer les logs de test ensuite.
4. Documenter l'outil dans `README.md` (section « Outils ») et dans la section
   « Commandes » de `CLAUDE.md`.
5. Si l'outil est destiné à être relancé souvent, proposer de créer un skill dédié.
