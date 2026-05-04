# Patch 2.A — Cloisonnement sectoriel de l'émargement

## Objectif
Empêcher qu'un utilisateur de secteur voie, ouvre, émarge ou génère des feuilles pour des ateliers / sessions d'un autre secteur.

## Correctifs principaux
- suppression du fallback dangereux `Numérique` dans le calcul du secteur courant ;
- ajout d'un contrôle centralisé d'accès secteur dans le module `activite` ;
- remplacement des comparaisons locales `atelier.secteur == secteur` / `session.secteur == secteur` par un contrôle basé sur `can_access_secteur(...)` ;
- verrouillage homogène des accès :
  - liste des activités ;
  - ouverture des sessions ;
  - émargement ;
  - ouverture / fermeture kiosque ;
  - génération et téléchargement des feuilles / archives ;
  - édition des ateliers et sessions.

## Effets métier
- un responsable de secteur sans `secteur_assigne` ne bascule plus par défaut sur le secteur Numérique ;
- un utilisateur ne peut plus accéder aux ateliers / sessions d'un autre secteur par URL directe ;
- les activités "seed" Numérique ne sont plus injectées pour un autre secteur par simple défaut implicite.

## Ajustements UX
- si aucun secteur n'est associé au compte, les vues activité / participants ne présentent plus de données d'un autre secteur par erreur ;
- les en-têtes affichent désormais `Aucun secteur sélectionné` quand le contexte secteur est absent.

## Fichiers touchés
- `app/activite/routes.py`
- `app/templates/activite/index.html`
- `app/templates/activite/participants.html`

## Contrôles réalisés
- compilation Python : OK

## Remarque
Le kiosque public par token reste public par conception : ce patch verrouille l'ouverture / gestion des kiosques côté utilisateurs authentifiés, pas la page publique d'accès par token/PIN.
