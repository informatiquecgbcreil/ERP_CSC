# Patch 2 — Référentiels dynamiques insertion

## Contenu
- passage des helpers insertion sur des permissions, plus sur le rôle `charge_insertion` ;
- ajout du CRUD complet des référentiels dynamiques :
  - dispositifs
  - prescripteurs
  - types de titre de séjour
  - diplômes linguistiques
  - niveaux
- sécurisation du CRUD par la permission `insertion:admin_refs` ;
- ajout d’écrans dédiés :
  - vue d’ensemble des référentiels
  - liste filtrable par référentiel
  - formulaire création / modification
- suppression contrôlée avec message propre si la valeur est encore utilisée ;
- mise à jour des pages d’accueil insertion et référentiels.

## Permissions utilisées
- `insertion:view` : accès au module
- `insertion:sensitive_view` : accès à la fiche insertion détaillée
- `insertion:admin_refs` : gestion des référentiels

## Pas de migration DB
Ce patch ne crée pas de nouvelle table et n’ajoute pas de migration Alembic.

## Fichiers touchés
- `app/services/insertion.py`
- `app/insertion/routes.py`
- `app/templates/insertion/index.html`
- `app/templates/insertion/referentiels.html`
- `app/templates/insertion/referentiel_list.html`
- `app/templates/insertion/referentiel_form.html`
