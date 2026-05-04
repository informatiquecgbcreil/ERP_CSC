# Patch UX lot 4 — recherche + statistiques quartiers

## Contenu du patch

### Recherche globale
- correction du bug de clic sur les filtres de type dans le panneau de recherche ;
- les filtres restent désormais utilisables sans fermer brutalement le panneau ;
- le focus revient dans le champ de recherche après clic sur un filtre ;
- ajout d'un lien vers la page complète `/recherche` depuis le panneau ;
- les facettes de type restent visibles même avant la relance complète de la recherche.

### Statistiques des quartiers
- ajout de filtres utiles : période, secteur, type de public ;
- gestion d'une période personnalisée avec dates de début / fin ;
- nouveaux indicateurs :
  - habitants suivis,
  - actifs sur la période,
  - présences,
  - nouveaux suivis,
  - ateliers touchés,
  - taux d'activité ;
- repère rapide rédigé en langage plus métier ;
- tableaux par secteur, atelier, chronologie mensuelle et personnes les plus vues ;
- bouton pour ouvrir directement les participants du quartier.

## Fichiers modifiés
- `app/templates/layout.html`
- `app/quartiers/routes.py`
- `app/templates/quartiers/stats.html`
