Patch P0.4G - Recentrage Pédagogie vers Suivi des apprentissages

Base utilisée : AppGestion.zip fournie le 30/04/2026 à 16h43.

Aucune migration.

À remplacer / ajouter :
- app/pedagogie/routes.py
- app/templates/layout.html
- app/templates/pedagogie/index.html
- app/templates/pedagogie/parcours.html
- app/templates/pedagogie/kiosk.html
- docs/pedagogie/P04G_RECENTRAGE_APPRENTISSAGES.md

Objectif :
- remplacer l’entrée “Pédagogie” par “Apprentissages” ;
- faire de /pedagogie/ une page simple “Suivi des apprentissages” ;
- ajouter /pedagogie/apprentissages comme alias du suivi simple ;
- créer /pedagogie/parcours si absent ;
- ne plus déduire automatiquement les éléments à observer depuis les projets/modules ;
- une séance n’observe que les apprentissages explicitement ajoutés.
