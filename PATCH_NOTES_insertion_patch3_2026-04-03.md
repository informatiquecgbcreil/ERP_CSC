# Patch 3 — Fiche insertion dédiée éditable — 2026-04-03

## Objectif
Rendre la fiche insertion **vraiment éditable** et séparer proprement :
- le **profil insertion**
- les **parcours**
- les **positionnements linguistiques**
- les **certifications linguistiques**

## Ce que le patch ajoute
- nouvelle table `participant_insertion_positionnement`
- enrichissement de `participant_insertion_certification` avec :
  - `parcours_id`
  - `date_passage`
  - `resultat`
- écran détail insertion enrichi
- écran d’édition de la fiche insertion
- formulaires dédiés pour :
  - ajout / modification d’un parcours
  - ajout / modification d’un positionnement
  - ajout / modification d’une certification
- suppression protégée (POST + CSRF) pour les 3 types d’entrées

## Règle métier posée
- **parcours** = cadre de suivi dans le temps
- **positionnement** = niveau constaté, avec ou sans diplôme
- **certification** = diplôme réellement présenté / obtenu

## Éditabilité
Oui :
- la fiche insertion dispose maintenant d’un bouton **Modifier la fiche insertion**
- le profil insertion est éditable
- les parcours sont ajoutables / modifiables / supprimables
- les positionnements sont ajoutables / modifiables / supprimables
- les certifications sont ajoutables / modifiables / supprimables

## Permissions
Le patch s’appuie sur :
- `insertion:view`
- `insertion:sensitive_view`
- `insertion:edit`
- `insertion:admin_refs`
- `insertion:export`

## Fichiers touchés
- `app/models.py`
- `app/services/insertion.py`
- `app/insertion/routes.py`
- `app/rbac.py`
- `app/templates/insertion/index.html`
- `app/templates/insertion/participant_detail.html`
- `app/templates/insertion/participant_edit.html`
- `app/templates/insertion/participant_parcours_form.html`
- `app/templates/insertion/participant_positionnement_form.html`
- `app/templates/insertion/participant_certification_form.html`
- `migrations/versions/22f3a4b5c6d7_insertion_positionnements_and_certif_enhancements.py`

## Contrôles faits
- compilation Python : OK
- compilation globale `compileall` : OK
- parsing Jinja des nouveaux templates : OK

## À faire après application
- redémarrer l’application
- laisser les migrations s’appliquer
- faire un `Ctrl+F5`

## Point d’attention
Les anciennes données legacy restent visibles. Lorsqu’une entrée legacy est modifiée depuis le nouveau module, elle bascule en pratique dans la logique **module insertion**.
