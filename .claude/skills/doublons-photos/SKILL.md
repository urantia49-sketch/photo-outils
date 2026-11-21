---
name: doublons-photos
description: Détecte les photos et vidéos en double (contenu identique) dans la photothèque Synology ou un dossier, et produit un rapport. Lecture seule. À utiliser quand l'utilisateur cherche des doublons, des copies, ou veut gagner de la place.
---

# Doublons photos

Script : `outils/trouver_doublons.py` (depuis la racine de photo-outils)

1. Déterminer le périmètre : une année
   (`/Users/remi/Library/CloudStorage/SynologyDrive-Photos/<année>`), toute la photothèque,
   ou un autre dossier. Recommander de commencer par une année.
2. Prévenir : le script lit le contenu complet des fichiers de même taille. Sur Synology Drive,
   les fichiers « à la demande » peuvent être téléchargés : c'est long sur un gros périmètre.
   Lancer en arrière-plan si nécessaire.
   ```bash
   python3 outils/trouver_doublons.py "<dossier>" --csv doublons_<nom>.csv
   ```
   (`--tous-fichiers` pour inclure les fichiers non médias.)
3. Résumer en français : nombre de groupes, copies en trop, espace récupérable, les 10 plus
   gros groupes. Pour chaque groupe, suggérer quelle copie garder (celle dans le dossier daté
   correspondant à sa date, plutôt que dans un dossier « vrac » ou « import »).
4. **Ne jamais supprimer.** Si l'utilisateur veut faire le ménage, proposer de déplacer les
   copies choisies dans un dossier `_doublons_a_supprimer/` à la racine de l'année, après
   confirmation fichier par fichier ou groupe par groupe, et le laisser supprimer lui-même.
