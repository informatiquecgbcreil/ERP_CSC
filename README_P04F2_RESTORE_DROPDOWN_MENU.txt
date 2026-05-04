Hotfix P0.4F.2 - Restauration du menu expert dropdown P0.3

Aucune migration.

À remplacer / ajouter :
- app/templates/layout.html
- app/static/css/p03e-responsive.css si présent dans le zip
- docs/pedagogie/P04F2_RESTAURE_MENU_DROPDOWN.md

Source utilisée pour restaurer le layout :
- P03E_responsive_mobile_tablette.zip

Correction :
- restaure le menu expert compact / dropdown automatique validé en P0.3 ;
- conserve le lien Pédagogie vers pedagogie.index (/pedagogie/) ;
- évite la régression vers l’ancien menu expert.
