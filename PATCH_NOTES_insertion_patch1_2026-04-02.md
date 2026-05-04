# Patch 1 — Module Insertion socioprofessionnelle (socle)

## Objet
Ce patch pose le socle technique du module **Insertion socioprofessionnelle** sans casser l'existant :
- nouvelles tables dédiées pour les données insertion sensibles ;
- migration douce depuis les champs legacy de `participant` ;
- durcissement d'accès pour réserver la lecture/édition au rôle **charge_insertion** ;
- ossature d'un module `insertion` séparé ;
- synchronisation transitoire entre l'ancien formulaire participant et les nouvelles tables.

## Fichiers principaux touchés
- `app/models.py`
- `app/rbac.py`
- `app/__init__.py`
- `app/participants/routes.py`
- `app/statsimpact/routes.py`
- `app/templates/layout.html`
- `app/templates/participants/form.html`
- `app/services/insertion.py`
- `app/insertion/routes.py`
- `app/templates/insertion/index.html`
- `app/templates/insertion/participant_detail.html`
- `app/templates/insertion/referentiels.html`
- `migrations/versions/21e2f3a4b5c6_insertion_module_foundation.py`

## Nouvelles tables
- `participant_insertion_profile`
- `participant_insertion_parcours`
- `participant_insertion_certification`
- `insertion_dispositif_ref`
- `insertion_prescripteur_ref`
- `insertion_titre_sejour_type_ref`
- `insertion_diplome_ref`
- `insertion_niveau_ref`

## Migration douce
La migration :
- crée les nouvelles tables ;
- recopie les données legacy déjà présentes sur `participant` vers les nouvelles tables ;
- ne supprime **pas encore** les anciennes colonnes du participant global ;
- marque les lignes migrées avec `legacy_source = true` pour ne pas écraser les futures vraies données du module insertion.

## Cloisonnement / RBAC
- nouveau rôle template : `charge_insertion`
- nouvelles permissions :
  - `insertion:admin_refs`
  - `insertion:export`
- le backend durcit l'accès sensible via des helpers dédiés :
  - formulaire participant insertion visible/éditable uniquement si l'utilisateur a le rôle `charge_insertion`
  - export nominatif insertion dans `statsimpact` réservé au rôle `charge_insertion`

## Module insertion (ossature)
Nouvelles routes :
- `/insertion/`
- `/insertion/participants/<participant_id>`
- `/insertion/referentiels`

Ce premier lot reste volontairement sobre : lecture / contrôle / préparation. Le CRUD complet des référentiels et la saisie dédiée arriveront dans les patchs suivants.

## Transition de l'ancien formulaire participant
Tant que les champs insertion legacy restent dans la fiche participant :
- les modifications sont encore saisies via l'ancien formulaire ;
- elles sont automatiquement recopiées vers les nouvelles tables ;
- l'anonymisation nettoie aussi les miroirs insertion correspondants.

## Important sur les rôles existants
Le bootstrap RBAC actuel **ne réécrit pas automatiquement les permissions des rôles déjà créés**, sauf si `RBAC_APPLY_TEMPLATES=1`.

Conséquence :
- le nouveau rôle `charge_insertion` sera bien créé ;
- mais si des rôles existants possédaient déjà des permissions insertion en base, il faudra les nettoyer via l'interface droits ou en réappliquant les templates dans un environnement maîtrisé.

## Contrôles effectués
- compilation Python : OK
- syntaxe Jinja des templates touchés : OK

## Suite logique
- Patch 2 : CRUD complet des référentiels dynamiques
- Patch 3 : fiche insertion dédiée (édition réelle)
- Patch 4 : exports insertion globaux / par prescripteur
- Patch 5 : émargement PDF trié par dispositif
