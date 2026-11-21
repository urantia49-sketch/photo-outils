#!/usr/bin/env python3
"""
Détecte les fichiers médias en double (contenu identique, quel que soit le nom)
dans une arborescence. Lecture seule : rien n'est supprimé ni déplacé.

Méthode : regroupement par taille, puis empreinte SHA-256 des fichiers de même taille.

Usage:
    python3 trouver_doublons.py <dossier> [--csv doublons.csv] [--tous-fichiers]

Exemple:
    python3 trouver_doublons.py "/Users/remi/Library/CloudStorage/SynologyDrive-Photos/2026" --csv doublons_2026.csv
"""

import argparse
import csv
import hashlib
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJET_DIR = Path(__file__).resolve().parent.parent
RESULTATS_DIR = PROJET_DIR / "resultats"
LOGS_DIR = PROJET_DIR / "logs"

MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif",
    ".cr2", ".cr3", ".nef", ".arw", ".dng", ".raf", ".orf", ".rw2",
    ".mov", ".mp4", ".m4v", ".avi",
}


def parse_args():
    p = argparse.ArgumentParser(description="Trouve les fichiers médias en double (lecture seule).")
    p.add_argument("root", type=Path, help="Dossier à analyser (récursivement)")
    p.add_argument("--csv", type=Path, default=None,
                   help=f"Exporte les groupes de doublons (chemin relatif => {RESULTATS_DIR})")
    p.add_argument("--tous-fichiers", action="store_true",
                   help="Analyse tous les fichiers, pas seulement les médias")
    return p.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def human(n: float) -> str:
    for unit in ("o", "Ko", "Mo", "Go", "To"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} Po"


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

    log(f"Recherche de doublons dans {root} — {now:%Y-%m-%d %H:%M:%S}\n")

    by_size = defaultdict(list)
    total = 0
    for f in root.rglob("*"):
        if not f.is_file() or f.name.startswith("."):
            continue
        if not args.tous_fichiers and f.suffix.lower() not in MEDIA_EXTENSIONS:
            continue
        total += 1
        by_size[f.stat().st_size].append(f)

    candidates = [paths for size, paths in by_size.items() if len(paths) > 1 and size > 0]
    n_hash = sum(len(p) for p in candidates)
    log(f"{total} fichier(s) analysé(s), {n_hash} à comparer par empreinte.")

    groups = []
    for i, paths in enumerate(candidates, 1):
        by_hash = defaultdict(list)
        for p in paths:
            try:
                by_hash[sha256(p)].append(p)
            except OSError as e:
                log(f"⚠️  illisible : {p} ({e})")
        groups.extend(g for g in by_hash.values() if len(g) > 1)
        if i % 50 == 0:
            print(f"  ... {i}/{len(candidates)} groupes de taille traités", file=sys.stderr)

    groups.sort(key=lambda g: g[0].stat().st_size * (len(g) - 1), reverse=True)
    wasted = sum(g[0].stat().st_size * (len(g) - 1) for g in groups)

    log("")
    for n, g in enumerate(groups, 1):
        log(f"Groupe {n} — {len(g)} copies de {human(g[0].stat().st_size)}")
        for p in sorted(g):
            log(f"    {p.relative_to(root)}")

    log(f"\n{len(groups)} groupe(s) de doublons, {sum(len(g) - 1 for g in groups)} copie(s) en trop, "
        f"{human(wasted)} récupérables.")

    if args.csv and groups:
        csv_path = args.csv if args.csv.is_absolute() else RESULTATS_DIR / args.csv
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["groupe", "taille_octets", "chemin"])
            for n, g in enumerate(groups, 1):
                for p in sorted(g):
                    w.writerow([n, p.stat().st_size, str(p.relative_to(root))])
        log(f"Détail écrit dans {csv_path}")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"doublons_{root.name}_{now:%Y%m%d_%H%M%S}.log"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"Synthèse écrite dans {log_path}")


if __name__ == "__main__":
    main()
