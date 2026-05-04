Patch P0.1B — Prévisionnel en onglets + création de subvention

Ce patch est cumulatif avec P0.1A.

Il ajoute :
- onglets Synthèse / Charges / Produits / Ventilation / Appels à projet ;
- séparation claire des charges et des produits ;
- bouton "Créer subvention" depuis une ligne produit ;
- lien entre BudgetPrevisionnelLigne et Subvention via subvention_id ;
- création automatique d'une ligne budgétaire produit dans la subvention créée ;
- rattachement automatique au projet si la ligne produit était associée à un projet.

Remplacer / ajouter les fichiers contenus dans ce zip à la racine de l'application.
Puis relancer Flask : les migrations 27 puis 28 doivent passer automatiquement.
