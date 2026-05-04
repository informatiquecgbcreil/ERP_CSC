Patch P0.4I - Écran séance complète

Base utilisée :
- AppGestion.zip fournie le 30/04/2026 à 16h43

Aucune migration.

À remplacer / ajouter :
- app/pedagogie/routes.py
- app/templates/layout.html
- app/templates/pedagogie/apprentissages.html
- app/templates/pedagogie/seance_complete.html
- docs/pedagogie/P04I_ECRAN_SEANCE_COMPLETE.md

Nouvelles routes :
- /pedagogie/
- /pedagogie/apprentissages
- /pedagogie/seance/<session_id>

Objectif :
- sélectionner une séance ;
- choisir les savoir-faire observés depuis le référentiel ;
- afficher les participants présents ;
- saisir les observations individuelles ;
- enregistrer les observations dans Evaluation ;
- commencer à relier les savoir-faire aux objectifs opérationnels.
