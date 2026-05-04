# Patch 4.A — Exports stats / bilans fidèles aux filtres

## Contenu

### Stats & Impact
- ajout d'un export **XLSX fidèle aux filtres actifs** :
  - route : `/stats-impact/export-fidele.xlsx`
  - bouton dans le dashboard
  - bouton dans la page Exports
- le fichier reprend le **périmètre exact** :
  - secteur demandé / secteur effectif
  - ateliers sélectionnés
  - bornes de dates
  - groupement
  - utilisateur et date d'export
- le classeur contient :
  - `Paramètres`
  - `Synthèse`
  - `Ateliers`
  - `Publics`
  - `Remplissage`
  - `Participants` (si les droits participants le permettent)
- la page Exports supporte maintenant la **multi-sélection d'ateliers** au lieu du seul `atelier_id` unique.

### Bilans et pilotage
- ajout d'un export **Excel fidèle à l'exercice et au scope courant** :
  - route : `/bilans/export.xlsx`
  - bouton `Export Excel fidèle` dans le dashboard bilans
- le classeur contient :
  - `Paramètres`
  - `Synthèse`
  - `Dépenses mensuelles`
  - `Par secteur`
  - `Alertes`

## Fichiers touchés
- `app/statsimpact/routes.py`
- `app/statsimpact/exports.html`
- `app/templates/statsimpact/dashboard.html`
- `app/bilans/routes.py`
- `app/templates/bilans_dashboard.html`

## Contrôles
- compilation Python : **OK**
- compileall global : **OK**

## Remarque
Ce lot pose le **socle export fidèle**. Il ne remplace pas encore les exports spécialisés existants (CSV, Magatomatique, DOCX bilans lourds) ; il les complète avec une version plus lisible et plus traçable du périmètre exporté.
