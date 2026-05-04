Hotfix P0.1H - contenu onglet Prévu vs réalisé

Symptôme : l'URL ?tab=realise fonctionne et le bouton est actif, mais aucun contenu n'apparaît.

Cause : la route autorisait enfin l'onglet, mais le bloc HTML {% if tab == 'realise' %} n'était pas présent dans detail.html.

Remplacer :
- app/previsionnel/routes.py
- app/templates/previsionnel/detail.html

Aucune migration.
