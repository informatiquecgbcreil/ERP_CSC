# Hotfix recherche page dédiée

- sécurise la route `/recherche` ;
- normalise les variables envoyées au template ;
- ajoute un fallback propre si le rendu principal plante ;
- rend `search_results.html` plus tolérant aux champs absents.
