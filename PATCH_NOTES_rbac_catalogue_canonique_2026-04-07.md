# Patch RBAC — catalogue canonique et écran Admin > Droits fiable

## Objectif
Mettre fin au décalage entre :
- les permissions réellement connues du code / de la base ;
- et celles visibles dans `admin_droits.html`.

## Ce que fait le patch
- complète le catalogue canonique des permissions avec les permissions insertion manquantes ;
- ajoute une liste d'alias legacy à masquer dans l'interface RBAC (`users:edit`, `bilan:view`, etc.) ;
- aligne les catégories RBAC sur des libellés stables et lisibles ;
- fait lire l'écran **Admin > Droits** depuis les permissions réellement présentes en base ;
- groupe les permissions par **catégorie réelle**, et non plus par préfixes codés en dur dans le template.

## Fichiers touchés
- `app/rbac.py`
- `app/admin/routes.py`
- `app/templates/admin_droits.html`

## Effet attendu
Après redémarrage :
- les permissions `insertion:*` apparaissent correctement ;
- `dashboard:view` apparaît dans **Accueil et navigation** ;
- les anciennes permissions alias ne polluent plus l'interface ;
- l'écran Admin > Droits colle enfin au catalogue réel.
