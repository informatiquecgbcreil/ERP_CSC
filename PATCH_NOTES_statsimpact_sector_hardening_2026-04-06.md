# Patch — Stats & Impact : durcissement final du cloisonnement inter-secteurs

Date : 2026-04-06

## Objectif
Éviter les dernières fuites inter-secteurs dans Stats & Impact, surtout pour les profils sectorisés, sans casser les écrans existants.

## Correctifs inclus

### 1. Secteur effectif forcé pour les profils sectorisés
- `normalize_filters(...)` force désormais le secteur de l'utilisateur quand il n'a pas `scope:all_secteurs` / `statsimpact:view_all`.
- Les `atelier_ids` passés dans l'URL sont nettoyés pour ne conserver que les ateliers du secteur autorisé.

### 2. Transversalité avancée neutralisée pour les accès sectorisés
- Pour un profil limité à un secteur, le bloc **Transversalité** n'expose plus d'indicateurs inter-secteurs.
- Plus de `top_cross` avec noms d'autres secteurs pour ces profils.
- Un message explicite est affiché à la place dans l'onglet Advanced.

### 3. Magatomatique / exports annuels recalés sur le scope réel
- Le calcul de `magatomatique_export` annuel par atelier s'appuie maintenant sur le secteur effectivement autorisé.

### 4. Stats pédagogie : liste participants resserrée au périmètre autorisé
- Les listes de participants proposées dans `stats/pedagogie` sont désormais filtrées sur le scope réellement visible.
- Plus de dropdown ou recherche qui remontent des participants hors secteur par simple présence dans la base.

## Fichiers touchés
- `app/statsimpact/engine.py`
- `app/statsimpact/routes.py`
- `app/templates/statsimpact/dashboard.html`
- `app/templates/statsimpact/_dashboard_body.html`

## Contrôles effectués
- compilation Python : OK
- compileall global : OK

## Remarque
Ce patch durcit le cloisonnement sans modifier les permissions RBAC existantes. Les profils multi-secteurs conservent les indicateurs croisés ; seuls les profils sectorisés voient ces blocs neutralisés.
