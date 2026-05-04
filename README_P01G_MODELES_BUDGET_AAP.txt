Patch P0.1G - Modèles de budgets et d'appels à projet

À remplacer/ajouter :
- app/previsionnel/routes.py
- app/previsionnel/referentiel.py
- app/templates/previsionnel/index.html
- app/templates/previsionnel/detail.html
- app/templates/previsionnel/referentiel.html
- migrations/versions/31c2d3e4f5a6_modeles_budgetaires_referentiel.py

Ce patch ajoute :
- modèles budgétaires dans le référentiel ;
- lignes de modèles basées sur les catégories du référentiel ;
- création d'un budget prévisionnel depuis un modèle ;
- anti-doublon si un modèle + catégories précochées contiennent la même ligne ;
- filtre par modèle dans l'onglet Appels à projet ;
- bouton pour cocher les lignes visibles dans un appel à projet.

Migration 31 : down_revision = 30b1c2d3e4f5.
Elle précharge trois modèles : Budget numérique standard, AAP CAF accès aux droits, AAP Politique de la ville.
