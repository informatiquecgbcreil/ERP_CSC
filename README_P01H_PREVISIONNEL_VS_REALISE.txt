Patch P0.1H - Prévisionnel vs réalisé

À remplacer :
- app/previsionnel/routes.py
- app/templates/previsionnel/detail.html

Aucune migration.

Ajoute :
- onglet Prévu vs réalisé dans un budget prévisionnel ;
- rapprochement par nature + compte + libellé, avec projet quand possible ;
- KPI charges prévues / exécutées ;
- KPI produits prévus / sécurisés ;
- lignes réelles non prévues ;
- tableau des écarts par ligne ;
- tableau des subventions réelles de l'exercice ;
- export XLSX dédié : /previsionnel/<id>/export-realise.xlsx ;
- correction du petit bug JS du filtre par modèle dans l'onglet Appels.

Note : ce rapprochement est volontairement non destructif. Il ne crée pas encore de liaison stricte en base.
