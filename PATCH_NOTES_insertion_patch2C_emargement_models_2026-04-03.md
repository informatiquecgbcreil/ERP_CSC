# Patch 2.C — Modèles d’émargement extensibles par secteur

## Objectif
Sortir de la logique « deux modèles codés en dur » pour permettre d’ajouter des **modèles d’émargement sectorisés** sans refaire une migration SQL ni casser l’existant.

## Ce que le patch ajoute
- un **registre de modèles d’émargement** stocké dans `instance/emargement_models.json`
- une interface de gestion dans le module Activité :
  - liste des modèles
  - ajout / modification / suppression
- trois moteurs disponibles immédiatement :
  - `Collectif standard`
  - `Individuel mensuel standard`
  - `Collectif par dispositif (N&B)`
- affectation d’un modèle collectif et d’un modèle individuel directement sur les **ateliers**
- nouveau lien **Modèles d’émargement** dans la page Activité

## Côté génération documentaire
- les valeurs stockées sur `AtelierActivite.modele_docx_collectif` et `modele_docx_individuel` peuvent désormais contenir un sélecteur `builtin:<cle>`
- le moteur `Collectif par dispositif (N&B)` :
  - trie les participants par **dispositif**, puis nom / prénom
  - ajoute une colonne texte **Dispositif**
  - génère une feuille compatible noir et blanc

## Important
- **aucune migration Alembic ajoutée** dans ce lot
- les anciens chemins de modèles DOCX personnalisés restent tolérés
- les modèles de base ne peuvent pas être supprimés, seulement réutilisés ou complétés par d’autres variantes

## Fichiers touchés
- `app/activite/routes.py`
- `app/activite/services/docx_utils.py`
- `app/activite/services/emargement_models.py` *(nouveau)*
- `app/templates/activite/index.html`
- `app/templates/activite/atelier_form.html`
- `app/templates/activite/emargement_models.html` *(nouveau)*
- `app/templates/activite/emargement_model_form.html` *(nouveau)*

## Contrôles réalisés
- compilation Python : **OK**
- parsing Jinja des templates modifiés : **OK**
