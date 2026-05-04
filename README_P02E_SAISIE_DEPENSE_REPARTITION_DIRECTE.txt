Patch P0.2E - Saisie d'une dépense avec répartition directe

À remplacer :
- app/budget/routes.py
- app/templates/depense_new.html
- app/templates/depense_edit.html

Aucune migration.

Ce patch améliore l'écran de création de dépense :
- la dépense reste unique ;
- une ligne de départ reste obligatoire pour compatibilité ;
- l'utilisateur peut répartir immédiatement le montant entre plusieurs sources ;
- sources possibles : lignes de subvention, fonds propres, autre ;
- si aucune répartition n'est saisie, l'ancien comportement reste : 100% sur la ligne de départ ;
- si la répartition est partielle, le reste peut être automatiquement complété sur la ligne de départ ;
- contrôle serveur pour empêcher une répartition supérieure au montant de la dépense.

Exemple : dépense 400€, répartition directe CAF 250€, QPV 100€, Fonds propres 50€.
