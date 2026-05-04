Patch P0.3C - Hubs métier

Base recommandée : AppGestion_Finance_Ready.zip + P0.3B.2 validé.

À remplacer / ajouter :
- app/main/routes.py
- app/templates/layout.html
- app/templates/hub_publics.html
- app/templates/hub_activites.html
- app/templates/hub_bilans.html
- app/templates/hub_ressources.html

Aucune migration.

Nouvelles routes :
- /publics
- /activites
- /bilans-hub
- /ressources

Objectif :
- transformer les grandes rubriques en vraies portes d'entrée métier ;
- garder le menu compact ;
- guider l'utilisateur vers les actions principales ;
- éviter que le menu soit le seul outil de navigation.

À tester :
- mode simple : Participants, Activités, Bilans ;
- mode expert : dropdowns Publics, Activités, Bilans, Ressources ;
- permissions limitées : les cartes doivent disparaître si l'utilisateur n'a pas les droits ;
- liens secondaires : ajout participant, doublons, suivi pédagogique, bilans lourds, inventaire, partenaires.
