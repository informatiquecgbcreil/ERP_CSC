Patch P0.2F - Dossier financeur vers subvention réelle

Objectif : intégrer l'étape réelle entre la demande de subvention et les dépenses :
- demandé ;
- attribué ;
- reçu ;
- enveloppe réellement imputable.

À remplacer :
- app/previsionnel/routes.py
- app/templates/previsionnel/appel_detail.html

Aucune migration.

Ce patch ajoute dans un dossier financeur / appel à projet :
- un bloc Réponse du financeur / subvention réelle ;
- création d'une subvention réelle depuis le dossier ;
- mise à jour d'une subvention déjà liée ;
- statut du dossier : préparation, envoyé, accordé, partiel, refusé, soldé ;
- synchronisation des lignes retenues vers les lignes budgétaires de la subvention ;
- répartition proportionnelle du montant attribué sur les charges retenues ;
- création du lien projet <-> subvention si le dossier est lié à un projet.
