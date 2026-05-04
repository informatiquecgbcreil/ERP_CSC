Hotfix P0.3B.2 - Fermeture automatique des menus déroulants

À remplacer :
- app/templates/layout.html

Aucune migration.

Correction :
- quand un menu déroulant s’ouvre, les autres se ferment ;
- clic en dehors du menu = fermeture ;
- clic sur un lien du menu = fermeture ;
- touche Échap = fermeture.

Objectif :
- conserver le menu compact du mode expert ;
- éviter d’avoir à recliquer sur le même bouton pour fermer ;
- éviter l’empilement visuel de plusieurs menus ouverts.
