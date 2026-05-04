# Patch 2.B hotfix — référentiels réels + clarification du parcours insertion

## Correctifs

### 1. Fiche participant : vrais référentiels insertion
Les champs transitoires suivants de la fiche participant globale utilisent désormais les référentiels insertion existants :
- Type de titre de séjour → `insertion_titre_sejour_type_ref`
- Diplôme linguistique → `insertion_diplome_ref`

Le comportement reste tolérant pendant la transition :
- les valeurs actives des référentiels sont proposées en priorité ;
- les anciennes valeurs déjà stockées sur `Participant` restent visibles si elles existent encore, pour ne pas casser l'édition de l'existant.

### 2. Clarification du vocabulaire
Le bloc de la fiche participant n'est plus présenté comme un « parcours insertion », ce qui prêtait à confusion.

Nouveaux libellés / aides :
- `Données insertion transitoires (sensibles)` sur la fiche participant ;
- précision que le **parcours insertion détaillé** sera géré dans la future fiche insertion dédiée ;
- `Diplôme linguistique` remplace `Diplôme obtenu` dans le bloc transitoire ;
- ajout d'une explication visible dans la fiche insertion dédiée sur la signification d'un **parcours insertion**.

## Fichiers modifiés
- `app/participants/routes.py`
- `app/templates/participants/form.html`
- `app/templates/insertion/participant_detail.html`

## Contrôles
- compilation Python : OK
