Patch P0.4J - Intention et bilan qualitatif portés par la séance

Patch cumulatif P0.4I + P0.4I.1 + P0.4J.

Base utilisée :
- AppGestion.zip fournie le 30/04/2026 à 16h43

Migration requise :
- python -m flask --app wsgi:app db upgrade

À remplacer / ajouter :
- app/models.py
- app/pedagogie/routes.py
- app/templates/layout.html
- app/templates/pedagogie/apprentissages.html
- app/templates/pedagogie/seance_complete.html
- migrations/versions/34f5a6b7c8d9_session_pedagogical_fields.py
- docs/pedagogie/P04J_SESSION_INTENTION_BILAN.md

Correction principale :
- l’intention de séance n’est plus créée comme Objectif ;
- elle est stockée dans session_activite ;
- ajout du bilan qualitatif animateur sur la séance ;
- les objectifs de séance existants sont copiés vers les nouveaux champs par la migration, sans suppression automatique.
