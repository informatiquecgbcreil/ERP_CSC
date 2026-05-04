Hotfix P0.3F.1 - Nettoyage des résultats d’audit navigation/templates

Aucune migration.

À remplacer :
- app/templates/admin_rbac_home.html
- app/templates/admin_rbac_roles.html
- app/templates/admin_rbac_role_edit.html
- app/templates/admin_rbac_users.html
- app/templates/ateliers_list.html
- app/templates/bilans_financeurs.html
- app/templates/bilans_subvention_print.html
- app/templates/insertion/participant_detail.html
- app/main/routes.py

Corrections réelles :
- anciens templates admin_rbac redirigés vers admin.droits/admin.users ;
- ateliers_list : lien sync_ateliers remplacé par activite.index ;
- bilans_financeurs / bilans_subvention_print : endpoints obsolètes remplacés ;
- insertion/participant_detail : participants.view_participant remplacé par participants.edit_participant.

Audit amélioré :
- ignore safe_url_for(...) au lieu de le confondre avec url_for(...) ;
- ne signale plus strftime dans les templates Jinja, car c’est souvent du formatage de date Python ;
- ignore les fichiers de copie/sauvegarde type ' - Copie.py' ;
- ne signale func.strftime que s’il semble non protégé par une logique SQLite/PostgreSQL.
