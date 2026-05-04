Hotfix P0.3F.2 - Correction endpoint ateliers.list_ateliers

Aucune migration.

Problème audit :
- app/ateliers/routes.py contenait un url_for('ateliers.list_ateliers') ;
- l’endpoint ateliers.list_ateliers n’est pas enregistré dans l’app actuelle ;
- l’entrée réelle utilisée pour ateliers/présences est activite.index.

Correction :
- remplacement de ateliers.list_ateliers par activite.index.

À remplacer :
- app/ateliers/routes.py
