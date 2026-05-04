Patch P0.3D + P0.3F - Vocabulaire harmonisé + audit navigation/templates

Aucune migration.

À remplacer / ajouter :
- app/templates/_vocab_finance.html
- app/templates/finance_home.html
- app/templates/finance_secteur.html
- app/templates/finance_simple.html
- app/templates/depense_new.html
- app/templates/bilans_secteur.html
- app/main/routes.py
- app/templates/controle_navigation.html
- app/templates/layout.html
- docs/navigation/P03D_VOCABULAIRE_HARMONISE.md
- docs/navigation/P03F_AUDIT_TECHNIQUE.md

P0.3D :
- harmonisation ciblée des termes visibles : enveloppe, demande de financement, répartition ;
- ajout d’un dictionnaire UI app/templates/_vocab_finance.html ;
- documentation docs/navigation/P03D_VOCABULAIRE_HARMONISE.md.

P0.3F :
- nouvelle route /controle/navigation ;
- audit des url_for des templates ;
- détection des has_perm résiduels ;
- détection de func.strftime côté Python ;
- lien Audit navigation ajouté dans le menu Admin/Contrôle si le layout contient le lien Contrôle.

Permission requise pour la page d’audit : controle:view.
