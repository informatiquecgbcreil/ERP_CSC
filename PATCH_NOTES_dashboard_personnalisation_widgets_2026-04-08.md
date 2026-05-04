# Patch dashboard personnalisation widgets — 2026-04-08

## Contenu
- ajout d'une personnalisation d'accueil par utilisateur ;
- raccourcis rapides configurables (jusqu'à 6) ;
- blocs du dashboard affichables / masquables et réordonnables ;
- bouton **Réinitialiser mon accueil** ;
- persistance en base du mode simple / expert ;
- libellés et icônes des actions rapides revus dans un style plus explicite.

## Fichiers principaux
- `app/models.py`
- `app/services/dashboard_customization.py`
- `app/services/dashboard_service.py`
- `app/main/routes.py`
- `app/templates/dashboard.html`
- `app/templates/dashboard_customize.html`
- `migrations/versions/24b5c6d7e8f9_user_dashboard_preferences.py`
