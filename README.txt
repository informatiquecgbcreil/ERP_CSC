Hotfix export XLSX prévisionnel

Remplacer :
- app/previsionnel/routes.py

Corrige le fichier Excel déclaré endommagé :
- les tableaux Excel démarraient sur la ligne vide juste avant les en-têtes ;
- Excel créait donc des colonnes de tableau nommées None ;
- la ligne d'en-tête est maintenant correctement repérée ;
- _add_table sécurise aussi les en-têtes vides ou dupliqués.

Relancer Flask puis retélécharger l'export budget prévisionnel.
