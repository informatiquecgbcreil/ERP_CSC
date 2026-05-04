# Patch menu uniformisé – 2026-04-09

Ce patch applique deux ajustements ciblés à partir de l'archive fournie :

- le ZIP est livré avec l'arborescence correcte du projet ;
- les intitulés du menu en mode complet sont harmonisés avec ceux du mode simple.

## Changements appliqués

### Navigation
- `Participants` -> `Personnes`
- `Projets` -> `Projets et actions`
- `Partenaires` -> `Annuaire partenaires`
- `Quartiers` -> `Villes et quartiers`
- `Insertion` -> `Suivi insertion`
- `Données ateliers` -> `Statistiques des ateliers`
- `Pédagogie` -> `Compétences et suivi`
- `Questionnaires` -> `Questionnaires d’impact`
- `Émargement` -> `Présences`
- `Inventaire` -> `Inventaire matériel`
- `Stats & bilans` -> `Bilans`
- `Bilans lourds` -> `Bilans détaillés`

### Mode d'affichage
- `Expert` -> `Complet`
- bannière mode simple alignée avec ce vocabulaire

### Breadcrumb / libellés internes
- labels module harmonisés avec les intitulés affichés dans le menu

## Fichier modifié
- `app/templates/layout.html`
