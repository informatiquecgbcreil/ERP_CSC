Hotfix merge heads Alembic prod

Symptome : Multiple head revisions are present for given argument 'head'.

Dans ta prod, les heads detectees sont :
- 29a0b1c2d3e4_budget_previsionnel_compte_long.py
- 31c2d3e4f5a6_modeles_budgetaires_referentiel.py

La base prod est actuellement sur :
- 29a0b1c2d3e4

Ce patch ajoute une migration de fusion :
- 32d3e4f5a6b7_merge_finance_heads_prod.py

Elle ne modifie pas les tables. Elle sert seulement a reunifier l'arbre Alembic.

A copier dans :
migrations/versions/

Puis relancer Flask. Alembic devrait appliquer les migrations manquantes 30 puis 31, puis valider la fusion 32.
