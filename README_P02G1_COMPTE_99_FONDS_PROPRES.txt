Patch P0.2G.1 - Compte 99 = Fonds propres / autofinancement interne

Aucune migration.

Principe retenu :
- on ne crée pas de table spéciale pour les fonds propres ;
- les fonds propres sont gérés comme une enveloppe de financement classique ;
- mais toute enveloppe ayant une ligne en compte 99 est isolée comme fonds propres / autofinancement ;
- une enveloppe nommée Fonds propres / autofinancement / reste à charge est également reconnue.

À remplacer :
- app/projets/routes.py
- app/templates/finance_secteur.html

Usage conseillé :
1. Créer dans le référentiel un compte interne : 99 - Fonds propres / autofinancement.
2. Créer une enveloppe de financement : Fonds propres 2026.
3. Ajouter une ligne de charge/imputation avec le compte 99.
4. Lors de la saisie des dépenses, imputer la part autofinancée sur cette enveloppe.
5. Le pilotage annuel l'isole automatiquement des subventions externes.

Note : compte 99 = convention analytique interne de l'application, pas compte comptable officiel.
