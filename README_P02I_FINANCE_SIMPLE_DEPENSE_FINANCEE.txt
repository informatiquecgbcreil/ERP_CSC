Patch P0.2I - Finance simplifiée + dépense financée

Aucune migration.

À remplacer / ajouter :
- app/projets/routes.py
- app/templates/finance_secteur.html
- app/templates/finance_simple.html

Nouvelle route : /finance/simple?secteur=Numérique&year=2026

Ajoute une vue simplifiée des enveloppes de financement et un formulaire de création de dépense financée.
La dépense est créée une seule fois et répartie immédiatement entre plusieurs enveloppes.
