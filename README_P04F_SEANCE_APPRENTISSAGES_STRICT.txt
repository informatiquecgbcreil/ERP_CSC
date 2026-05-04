Patch P0.4F - Séance et apprentissages explicites

Aucune migration.

À remplacer / ajouter :
- app/pedagogie/routes.py
- app/templates/pedagogie/parcours.html
- app/templates/pedagogie/kiosk.html
- app/templates/pedagogie/index.html
- docs/pedagogie/P04F_SEANCE_APPRENTISSAGES_STRICT.md

Changement majeur :
- le parcours simplifié et le kiosk n’affichent plus automatiquement les objectifs déduits depuis projets/modules/plans ;
- une séance affiche seulement les apprentissages explicitement rattachés à cette séance ;
- les anciens objectifs détectés deviennent des suggestions que l’utilisateur peut ajouter manuellement.

Objectif :
- arrêter les incohérences du type “séance MLVO → objectifs issus d’un autre projet” ;
- recentrer le module sur le geste terrain :
  séance → ce qu’on travaille → observation des participants → résultats.
