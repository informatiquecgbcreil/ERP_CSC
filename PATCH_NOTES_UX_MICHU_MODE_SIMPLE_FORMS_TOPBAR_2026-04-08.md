# Patch UX Michu – mode simple, topbar allégée, fiche participant rassurante

## Contenu du patch
- ajout d'un **mode d'affichage simple / expert** mémorisé en session utilisateur ;
- ajout d'une route `POST /ui-mode` pour basculer facilement d'un mode à l'autre ;
- topbar simplifiée en mode simple avec accès rapides centrés sur l'usage quotidien ;
- bannière explicite quand le mode simple est actif ;
- placeholder de recherche plus humain ;
- fiche participant entièrement réorganisée en sections :
  - informations essentielles,
  - adresse et rattachement,
  - informations complémentaires,
  - parcours insertion si habilitation ;
- aides micro-UX ajoutées sur les champs pour limiter le stress de saisie.

## Fichiers modifiés
- `app/__init__.py`
- `app/main/routes.py`
- `app/templates/layout.html`
- `app/templates/participants/form.html`

## Intention UX
Le patch vise une appropriation plus rapide par des profils peu technophiles :
- moins de surcharge cognitive au premier regard ;
- navigation recentrée sur les actions fréquentes ;
- formulation plus rassurante et plus concrète ;
- possibilité de repasser en mode expert sans rien perdre.

## Vérifications faites
- compilation Python : OK sur `app/__init__.py` et `app/main/routes.py` ;
- parsing Jinja : OK sur `layout.html` et `participants/form.html`.

## À tester côté instance
1. bascule simple/expert depuis la topbar ;
2. affichage du menu en mode simple puis en mode expert ;
3. création d'un participant ;
4. édition d'un participant existant ;
5. affichage lecture seule sur participant non éditable ;
6. recherche globale avec le nouveau placeholder.
