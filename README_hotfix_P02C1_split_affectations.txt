Hotfix P0.2C.1 - Split des affectations multi-financeurs

Problème corrigé :
- une dépense créée à 100% sur une première subvention bloquait ensuite l'ajout d'autres financeurs ;
- message : total affecté dépasserait le montant de la dépense.

Nouveau comportement :
- si le total est déjà à 100%, ajouter une nouvelle affectation réduit automatiquement l'affectation existante ;
- exemple : dépense 400€, CAF 400€ ; ajout QPV 100€ => CAF 300€ + QPV 100€ ;
- les affectations existantes sont maintenant modifiables directement depuis la fiche dépense.

À remplacer :
- app/budget/routes.py
- app/templates/depense_edit.html
- app/templates/depense_new.html

Aucune migration.
