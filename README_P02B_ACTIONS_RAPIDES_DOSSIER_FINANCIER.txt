Patch P0.2B - Actions rapides depuis le dossier financier projet

À remplacer :
- app/projets/routes.py
- app/templates/projet_finance.html
- app/templates/projets_list.html
- app/templates/projets_edit.html
- app/templates/_projet_budget_header.html

Aucune migration.

Ajoute dans /projets/<id>/finance :
- création rapide d'une charge projet ;
- création rapide d'un produit/financement projet ;
- création d'une subvention directement liée au projet ;
- rattachement d'une subvention existante au projet ;
- création rapide d'une dépense depuis une ligne de charge de subvention ;
- rattachement optionnel de la dépense à une charge projet.
