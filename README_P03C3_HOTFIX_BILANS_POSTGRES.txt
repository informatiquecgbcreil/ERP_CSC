Hotfix P0.3C.3 - Bilans compatibles PostgreSQL

À remplacer :
- app/bilans/routes.py
- app/bilans/services.py

Aucune migration.

Corrections :
1. Dashboard bilans :
   - suppression du abort(403) quand l'année passée dans l'URL n'est pas dans la liste initiale ;
   - l'année est ajoutée à la liste au lieu de faire tomber la page.

2. Série mensuelle des dépenses :
   - remplacement de func.strftime("%m", date_expr), spécifique SQLite ;
   - utilisation de extract("month", date_expr), compatible PostgreSQL et SQLite ;
   - conversion robuste du mois retourné par le dialecte.

Cause probable de l'erreur :
- PostgreSQL ne connaît pas la fonction SQLite strftime ;
- l'erreur apparaissait sur /bilans au moment de calculer compute_depenses_mensuelles().
