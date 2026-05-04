Hotfix P0.1H - onglet realise

Symptôme : clic sur 'Prévu vs réalisé' mais retour à la synthèse.

Cause : la route detail whitelist les onglets autorisés et ne contenait pas 'realise'.

Remplacer : app/previsionnel/routes.py

Aucune migration.
