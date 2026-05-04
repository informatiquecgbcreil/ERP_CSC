# Patch search/dashboard reconcile — 2026-04-08

## Corrigé
- réintégration du moteur de recherche enrichi dans `app/main/routes.py` ;
- restauration des recherches quartiers / ville / adresse / secteur / partenaires / projets / subventions / ateliers ;
- réajout de la page `search_results.html` ;
- correction du raccourci dashboard **Chercher un participant** pour qu'il ouvre la liste des participants au lieu de l'endpoint JSON `/participants/search` ;
- ajustement de quelques libellés / icônes des actions rapides ;
- nouvelle migration `25c6d7e8f9a0_search_perf_reconcile.py` pour remettre les index de recherche et les index trigram PostgreSQL sans collision avec la migration `24b5c6d7e8f9_user_dashboard_preferences.py`.

## À faire côté instance
1. appliquer la migration Alembic ;
2. redémarrer l'application ;
3. tester la barre de recherche globale et le raccourci dashboard ;
4. sur PostgreSQL, vérifier la présence de l'extension `pg_trgm` si la migration est passée.
