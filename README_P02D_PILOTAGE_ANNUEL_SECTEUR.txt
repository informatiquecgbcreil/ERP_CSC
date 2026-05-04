Patch P0.2D - Pilotage financier annuel du secteur

Objectif : créer une page centrale par année/secteur, adaptée au vrai cycle de gestion :
prévisionnel -> demandé -> accordé/reçu -> dépenses imputées.

À remplacer / ajouter :
- app/projets/routes.py
- app/templates/finance_secteur.html
- app/templates/projets_list.html
- app/templates/projet_finance.html

Nouvelle route :
- /finance/secteur?secteur=Numérique&year=2026

Aucune migration.

La page contient 5 onglets :
- Vue annuelle
- Budget
- Financeurs
- Projets
- Dépenses

Elle agrège :
- budgets prévisionnels du secteur ;
- dossiers financeurs/appels à projet ;
- subventions réelles ;
- dépenses uniques et affectations multi-financeurs ;
- fonds propres imputés ;
- alertes de base.
