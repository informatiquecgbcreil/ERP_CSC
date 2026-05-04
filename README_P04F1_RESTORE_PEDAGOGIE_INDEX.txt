Hotfix P0.4F.1 - Restauration de pedagogie.index

Aucune migration.

À remplacer / ajouter :
- app/pedagogie/routes.py
- app/templates/pedagogie/index.html
- docs/pedagogie/P04F1_RESTAURE_PEDAGOGIE_INDEX.md

Correction :
- restaure la route /pedagogie/ avec endpoint pedagogie.index ;
- corrige le BuildError qui faisait tomber le dashboard depuis le layout ;
- conserve le fonctionnement P0.4F : séance -> apprentissages explicites -> observation.
