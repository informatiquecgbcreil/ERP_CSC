Patch P0.2C - Imputation multi-financeurs des dépenses

Objectif : une dépense réelle reste unique, mais peut être répartie entre plusieurs sources : CAF, Politique de la ville, FONJEP, fonds propres, etc.

À remplacer / ajouter :
- app/models.py
- app/budget/routes.py
- app/projets/routes.py
- app/templates/depense_new.html
- app/templates/depense_edit.html
- app/templates/projet_finance.html
- migrations/versions/32d3e4f5a6b7_merge_finance_heads_prod.py
- migrations/versions/33e4f5a6b7c8_depense_affectations_multi_financeurs.py

Migration 33 : crée depense_affectation et migre les anciennes dépenses en affectation 100% sur leur ligne d'origine.
Le modèle ancien reste compatible : ligne_budget_id est conservé.

Usage : créer une dépense normalement, puis ouvrir sa fiche pour répartir le montant entre plusieurs enveloppes.
