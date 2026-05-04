Patch P0.2A - Dossier financier projet

Objectif : créer une page claire, graphique et compréhensible qui rassemble le budget prévu,
les financements, les dépenses et le réalisé d'un projet.

À remplacer / ajouter :
- app/projets/routes.py
- app/templates/projet_finance.html
- app/templates/projets_list.html
- app/templates/projets_edit.html
- app/templates/_projet_budget_header.html

Nouvelle route :
- /projets/<id>/finance

Aucune migration.

La page contient 5 onglets maximum :
- Vue d’ensemble
- Budget prévu
- Financements
- Dépenses & réalisé
- Exports

Cette version est volontairement non destructive : elle rassemble les données existantes sans changer les relations en base.
