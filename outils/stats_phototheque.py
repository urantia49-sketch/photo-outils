#!/usr/bin/env python3
"""
Statistiques sur la photothèque : nombre de fichiers et volume par année / type,
dossiers vides ou mal nommés, et (option --exif) répartition par appareil.
Lecture seule.

Usage:
    python3 stats_phototheque.py <dossier> [--exif]

<dossier> peut être la racine de la photothèque (sous-dossiers par année)
ou directement un dossier d'année (sous-dossiers AAAA-MM-JJ).

Exemple:
    python3 stats_phototheque.py "/Users/remi/Library/CloudStorage/SynologyDrive-Photos" --exif
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PROJET_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJET_DIR / "logs"

YEAR_RE = re.compile(r"^\d{4}$")
DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif",
    ".cr2", ".cr3", ".nef", ".arw", ".dng", ".raf", ".orf", ".rw2",
    ".mov", ".mp4", ".m4v", ".avi",
}


def parse_args():
    p = argparse.ArgumentParser(description="Statistiques sur la photothèque (lecture seule).")
    p.add_argument("root", type=Path, help="Racine de la photothèque ou dossier d'une année")
    p.add_argument("--exif", action="store_true",
                   help="Lit les métadonnées pour compter par appareil (plus lent)")
    return p.parse_args()


def human(n: float) -> str:
    for unit in ("o", "Ko", "Mo", "Go", "To"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} Po"


def year_dirs(root: Path):
    """Liste de (année, dossier). Si root est lui-même une année, le retourne seul."""
    if YEAR_RE.match(root.name):
        return [(root.name, root)]
    return [(d.name, d) for d in sorted(root.iterdir()) if d.is_dir() and YEAR_RE.match(d.name)]


def cameras(folder: Path) -> Counter:
    cmd = ["exiftool", "-r", "-j", "-fast2", "-Model", "-Make"]
    for ext in sorted(MEDIA_EXTENSIONS):
        cmd += ["-ext", ext.lstrip(".")]
    cmd.append(str(folder))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        print("Erreur: exiftool introuvable. Installez-le avec `brew install exiftool`.", file=sys.stderr)
        sys.exit(1)
    if not result.stdout.strip():
        return Counter()
    c = Counter()
    for e in json.loads(result.stdout):
        model = str(e.get("Model") or "").strip()
        make = str(e.get("Make") or "").strip()
        if model and make and not model.lower().startswith(make.split()[0].lower()):
            model = f"{make} {model}"
        c[model or "(inconnu)"] += 1
    return c


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

    years = year_dirs(root)
    if not years:
        print(f"Aucun dossier d'année (AAAA) trouvé dans {root}", file=sys.stderr)
        sys.exit(1)

    log(f"Statistiques de {root} — {now:%Y-%m-%d %H:%M:%S}\n")
    by_ext_total = Counter()
    size_by_ext = Counter()
    grand_files = grand_size = 0
    empty, misnamed, other_files = [], [], Counter()
    cams_total = Counter()

    log(f"{'Année':<8}{'Dossiers':>10}{'Fichiers':>10}{'Volume':>12}")
    for year, ydir in years:
        n_dirs = n_files = size = 0
        for d in sorted(ydir.iterdir()):
            if not d.is_dir():
                continue
            n_dirs += 1
            if not DATE_DIR_RE.match(d.name):
                misnamed.append(f"{year}/{d.name}")
            medias = 0
            for f in d.rglob("*"):
                if not f.is_file() or f.name.startswith("."):
                    continue
                ext = f.suffix.lower()
                if ext in MEDIA_EXTENSIONS:
                    s = f.stat().st_size
                    medias += 1
                    size += s
                    by_ext_total[ext] += 1
                    size_by_ext[ext] += s
                else:
                    other_files[ext or "(sans extension)"] += 1
            n_files += medias
            if medias == 0:
                empty.append(f"{year}/{d.name}")
        grand_files += n_files
        grand_size += size
        log(f"{year:<8}{n_dirs:>10}{n_files:>10}{human(size):>12}")
        if args.exif:
            cams_total += cameras(ydir)
    log(f"{'TOTAL':<8}{'':>10}{grand_files:>10}{human(grand_size):>12}\n")

    log("Par type de fichier :")
    for ext, n in by_ext_total.most_common():
        log(f"    {ext:<7}{n:>8}  {human(size_by_ext[ext]):>10}")

    if args.exif:
        log("\nPar appareil :")
        for cam, n in cams_total.most_common():
            log(f"    {cam:<35}{n:>8}")

    if other_files:
        log("\nFichiers non médias rencontrés : " + ", ".join(f"{e} ({n})" for e, n in other_files.most_common()))
    log(f"\nDossiers sans média ({len(empty)}) :")
    for d in empty:
        log(f"    {d}")
    log(f"\nDossiers sans date AAAA-MM-JJ en tête ({len(misnamed)}) :")
    for d in misnamed:
        log(f"    {d}")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"stats_{root.name}_{now:%Y%m%d_%H%M%S}.log"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"Synthèse écrite dans {log_path}")


if __name__ == "__main__":
    main()
