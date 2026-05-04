Hotfix P0.3C.4 - Correction has_perm undefined dans les templates bilans

À remplacer :
- app/templates/bilans_dashboard.html

Aucune migration.

Problème :
- bilans_dashboard.html utilisait has_perm("bilans:view") ;
- dans le contexte Jinja actuel, has_perm n’est pas disponible ;
- l’application utilise déjà can(...) dans le layout et les autres templates.

Correction :
- remplacement de has_perm(...) par can(...) dans les templates bilans concernés.
