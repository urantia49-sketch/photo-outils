#!/usr/bin/env python3
"""
Vérifie la cohérence entre le nom des dossiers photos (format AAAA-MM-JJ)
et la date de prise de vue (EXIF) des fichiers qu'ils contiennent.

Usage:
    python3 check_photo_dates.py <dossier_racine> [--tolerance N] [--csv sortie.csv]

Exemple:
    python3 check_photo_dates.py "/Users/remi/Library/CloudStorage/SynologyDrive-Photos/2026"
"""

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

DATE_DIR_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")

# Tags EXIF à essayer, dans l'ordre de préférence, pour la date de prise de vue.
DATE_TAGS = [
    "DateTimeOriginal",
    "CreateDate",
    "MediaCreateDate",
    "TrackCreateDate",
]

MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif",
    ".cr2", ".cr3", ".nef", ".arw", ".dng", ".raf", ".orf", ".rw2",
    ".mov", ".mp4", ".m4v", ".avi",
}


def parse_args():
    p = argparse.ArgumentParser(description="Détecte les incohérences entre dossiers datés et EXIF des photos.")
    p.add_argument("root", type=Path, help="Dossier racine contenant les sous-dossiers AAAA-MM-JJ (ex: le dossier 2026)")
    p.add_argument("--tolerance", type=int, default=0,
                   help="Écart en jours toléré entre la date du dossier et la date EXIF majoritaire (défaut: 0)")
    p.add_argument("--csv", type=Path, default=None, help="Écrit le détail des fichiers incohérents dans ce fichier CSV")
    return p.parse_args()


def find_dated_folders(root: Path):
    folders = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        m = DATE_DIR_RE.match(entry.name)
        if m:
            folders.append((entry, f"{m.group(1)}-{m.group(2)}-{m.group(3)}"))
    return folders


def read_dates_exiftool(folder: Path):
    """Retourne une liste de (nom_fichier, date_str ou None) pour chaque média du dossier."""
    files = [f for f in sorted(folder.iterdir())
             if f.is_file() and f.suffix.lower() in MEDIA_EXTENSIONS]
    if not files:
        return []

    cmd = ["exiftool", "-j", "-DateTimeOriginal", "-CreateDate",
           "-MediaCreateDate", "-TrackCreateDate"] + [str(f) for f in files]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print("Erreur: exiftool introuvable. Installez-le avec `brew install exiftool`.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Erreur exiftool sur {folder}: {e.stderr}", file=sys.stderr)
        return [(f.name, None) for f in files]

    data = json.loads(result.stdout)
    out = []
    for entry in data:
        name = Path(entry["SourceFile"]).name
        date_str = None
        for tag in DATE_TAGS:
            if tag in entry and entry[tag]:
                # Format exiftool: "2026:07:12 14:23:01" -> on garde juste AAAA-MM-JJ
                raw = entry[tag]
                dm = re.match(r"(\d{4}):(\d{2}):(\d{2})", raw)
                if dm and dm.group(1) != "0000":
                    date_str = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}"
                    break
        out.append((name, date_str))
    return out


def main():
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"Dossier introuvable: {root}", file=sys.stderr)
        sys.exit(1)

    folders = find_dated_folders(root)
    if not folders:
        print(f"Aucun dossier au format AAAA-MM-JJ trouvé dans {root}")
        return

    csv_rows = []
    total_issues = 0

    print(f"Analyse de {len(folders)} dossier(s) dans {root}\n")

    for folder, folder_date in folders:
        results = read_dates_exiftool(folder)
        if not results:
            print(f"⚠️  {folder.name}: aucun fichier média trouvé")
            continue

        no_exif = [name for name, d in results if d is None]
        dated = [(name, d) for name, d in results if d is not None]

        if not dated:
            print(f"⚠️  {folder.name}: aucune date EXIF lisible sur {len(results)} fichier(s)")
            total_issues += 1
            continue

        date_counts = Counter(d for _, d in dated)
        majority_date, majority_count = date_counts.most_common(1)[0]

        mismatches = [(name, d) for name, d in dated if d != folder_date]
        # Tolérance: si l'écart en jours est <= tolerance, on ne le compte pas comme mismatch
        if args.tolerance > 0 and mismatches:
            from datetime import date
            fy, fm, fd = map(int, folder_date.split("-"))
            folder_d = date(fy, fm, fd)
            filtered = []
            for name, d in mismatches:
                yy, mm, dd = map(int, d.split("-"))
                delta = abs((date(yy, mm, dd) - folder_d).days)
                if delta > args.tolerance:
                    filtered.append((name, d))
            mismatches = filtered

        status_bits = []
        if mismatches:
            status_bits.append(f"{len(mismatches)}/{len(dated)} fichier(s) avec une date EXIF différente du dossier")
        if no_exif:
            status_bits.append(f"{len(no_exif)} fichier(s) sans date EXIF")

        if not status_bits:
            print(f"✅ {folder.name}: OK ({len(dated)} fichiers, tous datés {folder_date})")
            continue

        total_issues += 1
        print(f"❌ {folder.name} (attendu {folder_date}): " + "; ".join(status_bits))

        # Détail des dates rencontrées
        other_dates = {d: c for d, c in date_counts.items() if d != folder_date}
        if other_dates:
            detail = ", ".join(f"{d} ({c}x)" for d, c in sorted(other_dates.items()))
            print(f"    dates EXIF trouvées: {detail}")

        for name, d in mismatches:
            csv_rows.append([folder.name, folder_date, name, d])
        for name in no_exif:
            csv_rows.append([folder.name, folder_date, name, "SANS_EXIF"])

    print(f"\n{total_issues} dossier(s) sur {len(folders)} présentent une incohérence.")

    if args.csv and csv_rows:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["dossier", "date_dossier", "fichier", "date_exif"])
            w.writerows(csv_rows)
        print(f"Détail écrit dans {args.csv}")


if __name__ == "__main__":
    main()
