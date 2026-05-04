# Patch notes — dashboard permission visibility — 2026-04-02

## Problème corrigé
La permission `dashboard:view` existait bien dans le RBAC, mais elle était rangée dans la catégorie générique **Autres**.
Dans la pratique, cela la rendait peu visible dans l'écran **Admin > Droits**, ce qui donnait l'impression qu'aucune permission dédiée au tableau de bord n'était cochable.

## Correctif appliqué
- recatégorisation de `dashboard:view` en **Accueil et navigation** ;
- conservation du code de permission existant (`dashboard:view`) ;
- au redémarrage, `bootstrap_rbac()` remet à jour la catégorie en base si nécessaire.

## Fichier touché
- `app/rbac.py`

## Résultat attendu
Après redémarrage de l'application et rechargement complet de la page **Admin > Droits** :
- un bloc **Accueil et navigation** apparaît ;
- la permission **`dashboard:view` — Accéder au tableau de bord** devient visible et cochable ;
- tu peux l'attribuer au rôle / profil de ton conseiller insertion.
