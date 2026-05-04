# Patch 2.B — Insertion : fin de la saisie libre + secteur attribuable dans le RBAC

## Objectif
Ce lot traite deux points bloquants avant la future fiche insertion dédiée :
1. empêcher la saisie libre sur deux champs insertion encore présents dans la fiche participant globale ;
2. permettre d'attribuer un **secteur** à n'importe quel rôle non global dans les écrans d'administration des droits.

## Changements

### 1) Fiche participant : fin de la saisie libre
Dans `app/templates/participants/form.html` :
- `Titre de séjour (type)` passe d'un champ texte libre à une **liste contrôlée** ;
- `Diplôme obtenu` passe d'un champ texte libre à une **liste contrôlée**.

Dans `app/participants/routes.py` :
- ajout du helper `_distinct_participant_values(...)` ;
- alimentation des listes depuis les **valeurs distinctes déjà présentes en base** sur `Participant` ;
- conservation de la valeur courante en édition, même si elle n'est plus fréquente.

⚠️ Important : sur **cette archive réelle**, les tables de référentiels insertion dédiées ne sont pas encore présentes. Ce patch supprime donc la saisie libre **sans réintroduire de migration ni de tables supplémentaires**. C'est une étape transitoire propre avant la fiche insertion séparée (Patch 3).

### 2) RBAC / utilisateurs : secteur attribuable hors seul rôle `responsable_secteur`
Dans `app/admin/routes.py` :
- ajout du helper `_roles_sector_policy(...)` ;
- un rôle ayant `scope:all_secteurs` est considéré comme **global** ;
- tous les autres rôles peuvent recevoir un `secteur_assigne` ;
- les routes `admin.droits` et `admin.set_user_roles` enregistrent maintenant aussi le secteur.

Dans `app/templates/admin_users.html` :
- la liste déroulante `Secteur assigné` n'est plus réservée au seul rôle `responsable_secteur` ;
- elle reste disponible pour tout rôle non global.

Dans `app/templates/admin_droits.html` :
- ajout d'un sélecteur `Secteur assigné` dans le bloc d'attribution des rôles par utilisateur ;
- activation / désactivation automatique selon la portée du rôle choisi.

## Fichiers touchés
- `app/participants/routes.py`
- `app/templates/participants/form.html`
- `app/admin/routes.py`
- `app/templates/admin_users.html`
- `app/templates/admin_droits.html`

## Contrôles
- compilation Python : OK
- parsing Jinja des templates modifiés : OK

## Limites assumées de ce lot
- les deux listes insertion sont pour l'instant alimentées par les **valeurs existantes** déjà connues dans la base ;
- l'admin complète de référentiels insertion dédiés reste à stabiliser dans la suite du chantier ;
- la vraie séparation métier arrivera avec le **Patch 3** (fiche insertion dédiée, parcours, certifications).
