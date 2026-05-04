# Hotfix 4.A — bouton et export fidèle sur `/bilan`

## Problème corrigé
Le bouton **Export Excel fidèle** avait été ajouté sur le dashboard du module `bilans` (`/bilans`), alors que l'écran réellement utilisé ici était le **bilan global** servi par `main.bilan_global()` sur **`/bilan`**.

## Correctifs
- ajout d'une route dédiée : `main.bilan_global_export_xlsx` sur `/bilan/export.xlsx`
- ajout du bouton **Export Excel fidèle** sur le template réellement affiché : `app/templates/bilan.html`
- extraction du calcul du bilan global dans un helper partagé pour éviter de changer le comportement de la page
- génération d'un classeur XLSX fidèle aux filtres actifs (`annee`, `secteur`, `projet_id`)

## Fichiers touchés
- `app/main/routes.py`
- `app/templates/bilan.html`

## Garanties
- aucun renommage des variables utilisées par les exports existants
- aucun impact voulu sur le Magatomatique
- aucun remplacement des exports CSV existants
