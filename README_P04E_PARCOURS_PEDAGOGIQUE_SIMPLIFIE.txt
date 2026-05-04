Patch P0.4E - Parcours pédagogique simplifié

Aucune migration.

À remplacer / ajouter :
- app/pedagogie/routes.py
- app/templates/pedagogie/index.html
- app/templates/pedagogie/parcours.html
- docs/pedagogie/P04E_PARCOURS_PEDAGOGIQUE_SIMPLIFIE.md

Nouvelle route :
- /pedagogie/parcours

Objectif :
- créer un parcours simple : Je prépare → J’évalue → Je regarde ;
- choisir une séance ;
- voir les objectifs détectés ;
- voir les modules/projets liés ;
- voir les participants présents ;
- lire les premiers résultats des suivis d’objectifs ;
- ouvrir le kiosk directement sur la séance.

Ce patch ne modifie pas la base de données et ne refond pas encore les calculs globaux.
