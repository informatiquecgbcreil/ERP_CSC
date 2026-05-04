# Hotfix patch 4.A — exports fidèles (2026-04-07)

## Corrigé
- ajout du helper manquant `_build_statsimpact_scope_workbook` dans `app/statsimpact/routes.py`
- l'export `statsimpact.export_fidele_xlsx` fonctionne sans casser les exports existants
- aucun renommage de variable, route ou export existant du Magatomatique
- réinclusion des éléments bilans pour l'export Excel fidèle :
  - route `bilans.dashboard_export_xlsx`
  - bouton `Export Excel fidèle` dans `app/templates/bilans_dashboard.html`

## Fichiers inclus
- `app/statsimpact/routes.py`
- `app/bilans/routes.py`
- `app/templates/bilans_dashboard.html`

## Vérification
- compilation Python OK
