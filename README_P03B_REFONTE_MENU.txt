Patch P0.3B - Refonte concrète du menu layout.html

Base : AppGestion_Finance_Ready.zip

À remplacer :
- app/templates/layout.html

Aucune migration.

Ce patch applique l'arborescence cible définie en P0.3A :
- menu simple plus lisible ;
- menu expert rangé par domaines métier ;
- Finances devient une porte d'entrée claire ;
- Public devient Publics & parcours ;
- Activité devient Activités & présences ;
- Bilans devient Bilans & exports ;
- Ressources et Administration sont séparés ;
- suppression du vieux lien admin en class dropdown-item ;
- ajout de petits intitulés dans les menus déroulants ;
- harmonisation partielle du fil d'Ariane.

Important :
- les routes ne sont pas renommées ;
- le serveur garde les mêmes protections RBAC ;
- le patch ne modifie que l'interface de navigation.
