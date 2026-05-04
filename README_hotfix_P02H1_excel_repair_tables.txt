Hotfix P0.2H.1 - Correction fichier XLSX réparé par Excel

Problème constaté :
- Excel ouvrait l'export XLSX en mode récupération/réparation ;
- le journal Excel indiquait une réparation d'un tableau /xl/tables/table*.xml.

Cause probable :
- les feuilles exportées cumulaient un autoFilter de feuille et un tableau structuré Excel ;
- ce chevauchement peut provoquer la réparation des tables par Excel.

Correction :
- suppression du filtre de feuille automatique dans _xlsx_style_sheet ;
- les feuilles avec données gardent un vrai tableau Excel filtrable/triable ;
- les feuilles sans données ne créent plus de table vide/header-only.

À remplacer :
- app/projets/routes.py

Aucune migration.
