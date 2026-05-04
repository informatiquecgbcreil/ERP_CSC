Patch P0.2J-K-L — Consolidation finance : garde-fous, contrôles, menu

Aucune migration.

À remplacer / ajouter :
- app/projets/routes.py
- app/budget/routes.py
- app/templates/finance_secteur.html
- app/templates/finance_simple.html
- app/templates/finance_home.html
- app/templates/layout.html

P0.2J — Garde-fous :
- empêche la création d'une dépense financée si une ligne/enveloppe n'a pas assez de reste disponible ;
- empêche l'ajout ou l'augmentation d'une affectation au-delà du reste d'une ligne ;
- garde l'auto-complétion, mais la contrôle avant enregistrement.

P0.2K — Cohérence :
- ajoute un moteur de contrôles dans le pilotage annuel ;
- détecte dépenses non équilibrées, enveloppes surconsommées, reçu > attribué, lignes surconsommées, dossiers accordés sans subvention réelle, sources libres hors enveloppe ;
- ajoute un onglet Contrôles ;
- l'export XLSX utilise les contrôles consolidés.

P0.2L — Navigation :
- ajoute une route /finance ;
- ajoute une page hub Finances ;
- ajoute des liens Vue simple / Pilotage / Contrôles ;
- regroupe plus clairement les entrées finance dans le menu.
