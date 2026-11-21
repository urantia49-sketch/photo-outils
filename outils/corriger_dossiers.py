#!/usr/bin/env python3
"""
Propose (et applique sur demande) le renommage des dossiers photos dont la date
(AAAA-MM-JJ en tête du nom) ne correspond pas à la date EXIF majoritaire des fichiers.

Par défaut : SIMULATION, aucun fichier n'est modifié. Ajouter --appliquer pour renommer.

Usage:
    python3 corriger_dossiers.py <dossier_racine> [--seuil 0.8] [--csv plan.csv] [--appliquer]

Exemple:
    python3 corriger_dossiers.py "/Users/remi/Library/CloudStorage/SynologyDrive-Photos/2026"
"""

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

PROJET_DIR = Path(__file__).resolve().parent.parent
RESULTATS_DIR = PROJET_DIR / "resultats"
LOGS_DIR = PROJET_DIR / "logs"

DATE_DIR_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
DATE_TAGS = ["DateTimeOriginal", "CreateDate", "MediaCreateDate", "TrackCreateDate"]
MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif",
    ".cr2", ".cr3", ".nef", ".arw", ".dng", ".raf", ".orf", ".rw2",
    ".mov", ".mp4", ".m4v", ".avi",
}


def parse_args():
    p = argparse.ArgumentParser(description="Renomme les dossiers datés selon la date EXIF majoritaire (simulation par défaut).")
    p.add_argument("root", type=Path, help="Dossier contenant les sous-dossiers AAAA-MM-JJ (ex: le dossier 2026)")
    p.add_argument("--seuil", type=float, default=0.8,
                   help="Part minimale des fichiers datés partageant la date majoritaire pour proposer un renommage (défaut: 0.8)")
    p.add_argument("--csv", type=Path, default=None,
                   help=f"Exporte le plan de renommage (chemin relatif => {RESULTATS_DIR})")
    p.add_argument("--appliquer", action="store_true",
                   help="Effectue réellement les renommages (sinon simulation)")
    return p.parse_args()


def read_dates(folder: Path):
    files = [f for f in sorted(folder.iterdir()) if f.is_file() and f.suffix.lower() in MEDIA_EXTENSIONS]
    if not files:
        return []
    cmd = ["exiftool", "-j"] + [f"-{t}" for t in DATE_TAGS] + [str(f) for f in files]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print("Erreur: exiftool introuvable. Installez-le avec `brew install exiftool`.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Erreur exiftool sur {folder}: {e.stderr}", file=sys.stderr)
        return [None for _ in files]
    dates = []
    for entry in json.loads(result.stdout):
        found = None
        for tag in DATE_TAGS:
            m = re.match(r"(\d{4}):(\d{2}):(\d{2})", str(entry.get(tag) or ""))
            if m and m.group(1) != "0000":
                found = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                break
        dates.append(found)
    return dates


def main():
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"Dossier introuvable: {root}", file=sys.stderr)
        sys.exit(1)

    now = datetime.now()
    log_lines = []

    def log(msg=""):
        print(msg)
        log_lines.append(msg)

    mode = "APPLICATION" if args.appliquer else "SIMULATION (aucune modification)"
    log(f"Correction des dossiers de {root} — {now:%Y-%m-%d %H:%M:%S} — mode {mode}")
    log(f"Seuil de majorité : {args.seuil:.0%}\n")

    plan = []  # (ancien, nouveau, date_dossier, date_exif, part, statut)
    folders = [d for d in sorted(root.iterdir()) if d.is_dir() and DATE_DIR_RE.match(d.name)]
    for folder in folders:
        folder_date = "-".join(DATE_DIR_RE.match(folder.name).groups())
        dates = [d for d in read_dates(folder) if d]
        if not dates:
            continue
        majority, count = Counter(dates).most_common(1)[0]
        if majority == folder_date:
            continue
        share = count / len(dates)
        new_name = majority + folder.name[10:]
        if share < args.seuil:
            statut = "ignoré (majorité insuffisante)"
        elif (root / new_name).exists():
            statut = "conflit (le dossier cible existe déjà)"
        else:
            statut = "à renommer"
        plan.append([folder.name, new_name, folder_date, majority, f"{share:.0%}", statut])

    if not plan:
        log("Aucun dossier à corriger.")
    renamed = 0
    for row in plan:
        old, new, _, _, share, statut = row
        icon = {"à renommer": "➡️ "}.get(statut, "⚠️ ")
        log(f"{icon} {old}  →  {new}   [{share} des fichiers] {statut}")
        if statut == "à renommer" and args.appliquer:
            try:
                (root / old).rename(root / new)
                row[5] = "renommé"
                renamed += 1
            except OSError as e:
                row[5] = f"échec: {e}"
                log(f"    échec : {e}")

    todo = sum(1 for r in plan if r[5] in ("à renommer", "renommé"))
    log("")
    if args.appliquer:
        log(f"{renamed} dossier(s) renommé(s) sur {todo} prévu(s).")
    else:
        log(f"{todo} dossier(s) seraient renommés. Relancer avec --appliquer pour effectuer les changements.")

    if args.csv and plan:
        csv_path = args.csv if args.csv.is_absolute() else RESULTATS_DIR / args.csv
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ancien_nom", "nouveau_nom", "date_dossier", "date_exif_majoritaire", "part", "statut"])
            w.writerows(plan)
        log(f"Plan écrit dans {csv_path}")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "appliquer" if args.appliquer else "simulation"
    log_path = LOGS_DIR / f"corriger_{root.name}_{suffix}_{now:%Y%m%d_%H%M%S}.log"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"Synthèse écrite dans {log_path}")


if __name__ == "__main__":
    main()
