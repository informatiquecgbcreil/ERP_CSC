Patch P0.4D - Kiosk : objectifs attendus par session

Aucune migration.

À remplacer / ajouter :
- app/pedagogie/routes.py
- app/templates/pedagogie/kiosk.html
- app/templates/pedagogie/index.html
- app/templates/layout.html
- docs/pedagogie/P04D_KIOSK_OBJECTIFS_SESSION.md

Corrections incluses :
1. Le menu “Pédagogie” pointe vers /pedagogie/ au lieu de l’ancienne page des référentiels.
2. Le kiosk pédagogique récupère désormais les objectifs attendus par plusieurs chemins :
   - projet lié à l’atelier ;
   - objectifs généraux du projet ;
   - objectifs spécifiques de l’atelier ;
   - objectifs enfants ;
   - objectifs de la session ;
   - objectifs des modules de session ;
   - objectifs des modules de l’atelier ;
   - objectifs des modules du plan Projet → Atelier → Module.

Objectif :
- faire remonter les objectifs opérationnels créés via modules / plan pédagogique dans le kiosk de la séance.
