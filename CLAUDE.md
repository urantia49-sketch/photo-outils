# photo-outils

Scripts Python pour vérifier et organiser la photothèque stockée sur Synology Drive
(`/Users/remi/Library/CloudStorage/SynologyDrive-Photos/<année>/<AAAA-MM-JJ ...>/`).

## Structure

- `outils/` — un script autonome par outil (`check_photo_dates.py`, ...)
- `logs/` — synthèse de chaque exécution (`<dossier>_<horodatage>.log`), ignoré par git
- `resultats/` — exports CSV, ignoré par git

## Conventions

- Python 3, **bibliothèque standard uniquement** (pas de pip) ; les métadonnées passent par
  `exiftool` appelé en sous-processus (`-json`).
- Chaque outil : docstring d'usage en tête, `argparse`, sortie console lisible en français,
  log dans `logs/`, CSV optionnel dans `resultats/` (chemins relatifs à la racine du projet).
- **Lecture seule par défaut** sur la photothèque. Tout outil qui renomme/déplace des
  fichiers doit avoir un mode `--dry-run` activé par défaut et une option explicite pour appliquer.
- Documenter chaque nouvel outil dans `README.md`.

## Commandes

```bash
python3 outils/check_photo_dates.py "<dossier_année>" [--tolerance N] [--csv sortie.csv]
python3 outils/corriger_dossiers.py "<dossier_année>" [--seuil 0.8] [--csv plan.csv] [--appliquer]
python3 outils/trouver_doublons.py "<dossier>" [--csv doublons.csv] [--tous-fichiers]
python3 outils/stats_phototheque.py "<photothèque ou année>" [--exif]
python3 -m py_compile outils/*.py   # vérification syntaxe rapide
```

Python système = 3.9 : pas de `X | Y` dans les annotations ni de `match`.

Skills : `/verifier-dates-photos`, `/corriger-dossiers-photos`, `/doublons-photos`,
`/stats-phototheque`, `/nouvel-outil-photo`.

## En cours / À faire

- (2026-11-21) Nouveaux outils (corriger_dossiers, trouver_doublons, stats_phototheque) testés
  sur une photothèque factice uniquement : premier passage réel à faire, en commençant par
  `/stats-phototheque` puis `/verifier-dates-photos` sur 2026.
