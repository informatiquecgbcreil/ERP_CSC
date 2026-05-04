Patch P0.1F — Référentiel branché sur subventions, dépenses et budgets d’appel

Base utilisée : archive fournie "previsionnel avance.zip".

À remplacer :
- app/main/routes.py
- app/budget/routes.py
- app/templates/subventions_list.html
- app/templates/budget_pilotage.html
- app/templates/depense_new.html
- app/templates/depense_edit.html
- app/templates/previsionnel/detail.html

Nouveautés :
1) Subventions
- Le formulaire de création d’une subvention peut pré-créer des lignes budgétaires depuis le référentiel.
- Dans le pilotage d’une subvention, l’ajout de ligne peut utiliser une ligne type du référentiel.
- Les lignes existantes peuvent aussi être modifiées en choisissant une ligne type.
- Le compte, le libellé, la nature et le montant par défaut sont préremplis.

2) Dépenses
- La création d’une dépense propose une catégorie de dépense issue du référentiel.
- La catégorie préremplit le libellé et le type de dépense.
- La modification d’une dépense propose le même confort.
- La dépense reste rattachée à une ligne budgétaire de charge comme avant.

3) Budgets d’appel à projet
- Dans l’onglet Appels à projet du prévisionnel, ajout d’un filtre par nature / compte / catégorie du référentiel.
- Bouton pour cocher automatiquement les lignes visibles.
- Aucun stockage supplémentaire : on aide la sélection sans casser la logique existante.

Aucune migration nécessaire.
