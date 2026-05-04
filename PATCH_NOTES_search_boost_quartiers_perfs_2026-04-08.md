# Patch recherche globale – 2026-04-08

## Améliorations fonctionnelles
- ajout des **quartiers** dans la recherche globale (type dédié + recherche dans les fiches participants)
- recherche élargie sur davantage de champs : adresses, villes, téléphones, mails, secteur, contacts partenaires
- enrichissement des métadonnées affichées dans les résultats
- ajout de filtres visuels par type et par secteur
- ajout d'une page **/recherche** pour afficher tous les résultats d'une requête
- aide rapide au focus avec raccourcis cliquables

## Améliorations performance
- moteur de recherche en **3 passes** : exact / préfixe / contient
- limitation plus intelligente des candidats remontés par type
- ajout d'index SQL ciblés sur les champs les plus consultés
- ajout d'index trigram PostgreSQL (si PostgreSQL) pour mieux encaisser les grosses bases

## Filtres supportés
- `type:participant`
- `type:quartier`
- `secteur:NomDuSecteur`
- `quartier:Rouher`
