Hotfix P0.3C.2 - Bilans années + lisibilité des tableaux

À remplacer :
- app/bilans/routes.py
- app/bilans/services.py
- app/templates/bilans_secteur.html
- app/templates/bilans_subvention.html

Aucune migration.

Corrections :
1. Filtre année :
   - la liste des années ne dépend plus uniquement des sessions ;
   - elle inclut aussi les années d’exercice des subventions/enveloppes ;
   - sélectionner une année absente de la liste initiale n’entraîne plus d’abort brutal ;
   - secteur/subvention invalide après changement d’année = retour propre vers la première donnée disponible.

2. Bilan par secteur :
   - remplacement du tableau lignes budgétaires par des lignes/cartes lisibles ;
   - colonnes budget/engagé/reste/taux plus stables ;
   - barre de consommation par ligne ;
   - meilleure adaptation ordinateur/tablette/mobile.

3. Bilan par subvention/enveloppe :
   - affichage plus lisible des dépenses imputées ;
   - cartes KPI ;
   - matériel lié affiché en cartes.

But :
- éviter les erreurs type 403/503 au changement d’année ;
- supprimer les tableaux éclatés façon accordéon cassé.
