Hotfix P0.3C.1 - Hub bilans + lisibilité dépenses

À remplacer :
- app/main/routes.py
- app/budget/routes.py
- app/templates/depenses_list.html

Aucune migration.

Corrections :
1. Hub Bilans :
   - correction de l’endpoint export XLSX :
     main.bilan_export_xlsx -> main.bilan_global_export_xlsx

2. Liste des dépenses :
   - ajout recherche texte ;
   - ajout filtre exercice ;
   - ajout pagination 20 / 50 / 100 / 200 ;
   - total filtré calculé côté serveur ;
   - regroupement visuel par mois ;
   - affichage plus lisible fournisseur / référence ;
   - libellé “Enveloppe” au lieu de “Subvention” ;
   - bouton “Dépense financée” vers la vue simple finance.

But :
- éviter le mur de dépenses interminable ;
- rendre la liste exploitable quand la base grossit.
