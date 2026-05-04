# Patch 2.B hotfix — restauration du module insertion

## Problème corrigé
Le patch 2.B avait été construit sur une base incomplète :
- disparition du blueprint `app/insertion`
- disparition des templates du module insertion
- disparition des modèles Python du module insertion
- perte des permissions `insertion:admin_refs` et `insertion:export`
- disparition du lien **Insertion** dans le menu principal

## Ce que fait ce hotfix
- restaure le module `app/insertion`
- restaure les modèles et le service backend liés à l’insertion
- rebranche le blueprint insertion dans `app/__init__.py`
- restaure la migration `21e2f3a4b5c6_insertion_module_foundation.py`
- restaure les permissions insertion manquantes dans le RBAC
- remet le menu **Insertion** sur une logique **permission-based** (`insertion:view`) et non sur le rôle `charge_insertion`
- conserve les améliorations du patch 2.B :
  - sélecteurs contrôlés pour `titre_sejour_type` et `diplome_obtenu`
  - attribution de secteur possible pour les rôles non globaux
- ajoute les tokens CSRF manquants sur les formulaires POST des référentiels insertion
- rétablit la synchronisation transitoire des anciens champs insertion de `Participant` vers le nouveau module

## Fichiers principaux touchés
- `app/__init__.py`
- `app/models.py`
- `app/rbac.py`
- `app/services/insertion.py`
- `app/insertion/*`
- `app/templates/layout.html`
- `app/templates/insertion/*`
- `app/templates/participants/form.html`
- `app/participants/routes.py`
- `migrations/versions/21e2f3a4b5c6_insertion_module_foundation.py`

## Contrôles effectués
- compilation Python : OK

## Après application
- redémarrer l’application
- faire un `Ctrl+F5`
- vérifier dans **Admin > Droits** que le bloc **Insertion** est revenu
- attribuer au besoin :
  - `insertion:view`
  - `insertion:edit`
  - `insertion:sensitive_view`
  - `insertion:admin_refs`
  - `insertion:export`
