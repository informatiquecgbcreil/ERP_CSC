Patch P0.1A — Prévisionnel financier global + extraction appel à projet

À remplacer / ajouter :
- app/models.py
- app/__init__.py
- app/templates/layout.html
- app/previsionnel/__init__.py
- app/previsionnel/routes.py
- app/templates/previsionnel/index.html
- app/templates/previsionnel/detail.html
- app/templates/previsionnel/appel_detail.html
- migrations/versions/27e8f9a0b1c2_budget_previsionnel.py

Ce premier lot ajoute :
- une entrée Prévisionnel dans le menu ;
- création d'un budget prévisionnel global par année/secteur ;
- lignes charge/produit avec compte, projet, montant, commentaire ;
- décomposition automatique par projet ;
- export XLSX du budget global ;
- création d'un budget d'appel à projet en sélectionnant des lignes du prévisionnel ;
- export XLSX du budget d'appel à projet.

Relance ensuite Flask : la migration se lancera au démarrage comme les précédentes.
