Patch P0.2G - Fonds propres + clarification du cycle financeur

Aucune migration.

Objectifs :
- clarifier l'onglet Appels à projet du prévisionnel : étape 1 = préparer une demande ;
- clarifier le détail d'un dossier financeur : étape 2 = saisir la réponse réelle ;
- rappeler la différence entre demande, subvention réelle, reçu et dépenses imputées ;
- rendre les fonds propres / l'autofinancement plus visibles dans le pilotage annuel ;
- clarifier les écrans de dépense autour des affectations multi-financeurs.

À remplacer :
- app/templates/previsionnel/detail.html
- app/templates/previsionnel/appel_detail.html
- app/templates/finance_secteur.html
- app/templates/depense_new.html
- app/templates/depense_edit.html

Ce patch ne change pas encore le modèle de données : fonds propres reste une source d'affectation.
La vraie enveloppe formelle 'Fonds propres 2026' pourra venir plus tard si besoin.
