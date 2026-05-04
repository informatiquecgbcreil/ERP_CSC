Patch P0.2H - Export XLSX du pilotage financier annuel

Aucune migration.

À remplacer :
- app/projets/routes.py
- app/templates/finance_secteur.html

Nouvelle route :
- /finance/secteur/export.xlsx?secteur=Numérique&year=2026

Ce patch ajoute un bouton Export XLSX dans le pilotage annuel du secteur.

Le fichier exporté contient :
- Lecture rapide ;
- Budgets ;
- Comptes prévisionnels ;
- Financeurs externes ;
- Fonds propres 99 ;
- Sources imputées ;
- Dossiers financeurs ;
- Projets ;
- Dépenses ;
- Affectations dépenses ;
- Contrôles.

Les feuilles sont formatées en vrais tableaux Excel filtrables / triables quand c'est pertinent.
Les titres de feuilles et de tableaux sont sécurisés pour éviter les erreurs Excel.
