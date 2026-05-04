Hotfix P0.4E.1 - Suppression sécurisée des objectifs

Aucune migration.

À remplacer / ajouter :
- app/pedagogie/routes.py
- app/templates/pedagogie/objectifs.html
- docs/pedagogie/P04E1_SUPPRESSION_OBJECTIFS_SECURISÉE.md

Correction :
- un objectif déjà utilisé dans objectif_suivi ne peut plus provoquer d’IntegrityError ;
- un objectif avec des enfants ne peut plus être supprimé directement ;
- la page affiche “Utilisé” au lieu du bouton Supprimer quand l’objectif est déjà rattaché à l’historique ;
- les liens de compétences sont nettoyés avant suppression pour les objectifs non utilisés.

Important :
- il n’y a pas encore d’archivage d’objectif, faute de colonne dédiée ;
- on bloque donc la suppression des objectifs utilisés pour préserver l’historique.
