# Patch 3.A — Cloisonnement statsimpact + secteur de création participant + dates du titre de séjour

## Corrections
- Stats Impact (onglet Advanced) : durcissement du cloisonnement secteur sur les blocs d'occupation et les listes d'ateliers.
- Création / édition participant : champ `Secteur de création` désormais piloté par la liste des secteurs actifs administrés, au lieu d'un texte libre.
- Module insertion : ajout des champs `date_debut_titre_sejour` et `date_expiration_titre_sejour` sur le parcours insertion.

## Fichiers touchés
- `app/statsimpact/occupancy.py`
- `app/statsimpact/routes.py`
- `app/participants/routes.py`
- `app/templates/participants/form.html`
- `app/models.py`
- `app/insertion/routes.py`
- `app/templates/insertion/participant_parcours_form.html`
- `app/templates/insertion/participant_detail.html`
- `app/templates/insertion/participant_edit.html`
- `migrations/versions/23a4b5c6d7e8_insertion_titre_sejour_dates_and_scope_tweaks.py`

## Note
Le champ secteur de création reste automatiquement verrouillé au secteur courant pour les profils non globaux.
