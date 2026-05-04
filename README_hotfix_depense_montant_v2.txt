Hotfix depense montant v2

Corrige le bug des centimes fantomes type 155 -> 155.01.

Remplacer :
- app/budget/routes.py
- app/templates/depense_new.html
- app/templates/depense_edit.html

Corrections :
- suppression du value=0.01 dans la creation de depense ;
- champs montant en texte + clavier decimal ;
- parsing serveur avec Decimal ;
- accepte 155, 155.00, 155,00, 1 255,50, 155 € ;
- valeur unitaire inventaire securisee aussi.

Aucune migration necessaire.
