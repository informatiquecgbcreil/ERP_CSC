# Audit UI / simplicité d’usage (public non expert)

Date : 10 avril 2026  
Périmètre : parcours web principal (connexion, navigation, dashboard, formulaires, tableaux)  
Méthode : audit heuristique UX + accessibilité (inspiré WCAG 2.2 AA) basé sur revue des templates/CSS.

## 1) Verdict rapide

- **Niveau global actuel : intermédiaire** (beaucoup d’éléments positifs, mais plusieurs obstacles pour publics fragiles).
- **Pour utilisateurs peu à l’aise avec le numérique** : l’application est utilisable, mais la densité d’actions et la navigation “en pastilles” augmentent la charge cognitive.
- **Pour troubles de lecture (dyslexie, fatigue cognitive)** : vocabulaire globalement simple, mais taille de police parfois petite et écrans parfois trop chargés.
- **Pour troubles visuels** : thèmes clair/sombre présents (bon point), mais certains contrastes/tailles/focus restent à sécuriser systématiquement.

## 2) Forces observées

1. **Deux thèmes (clair/sombre) et persistance locale** : bon levier pour le confort visuel.
2. **Champs de formulaires avec focus visuel** : réduit les erreurs d’entrée.
3. **Messages flash avec `aria-live`** : meilleure annonce des retours système.
4. **Aides textuelles présentes sur la connexion et dashboard** : utile pour primo-utilisateurs.
5. **Version “mode simple” déjà amorcée dans le dashboard** : excellente base pour une UX inclusive.

## 3) Risques UX/accessibilité (priorisés)

### Critique (P1)

1. **Navigation principale trop dense**
   - Beaucoup d’entrées simultanées en topbar (plus emojis, labels longs, modules multiples).
   - Impact : désorientation des non-experts, difficulté à “savoir où cliquer”.

2. **Absence explicite d’un lien “Aller au contenu” (skip link)**
   - Le clavier doit traverser de nombreux éléments avant le contenu.
   - Impact fort pour utilisateurs clavier, lecteurs d’écran, troubles moteurs.

3. **Cibles tactiles possiblement petites (pastilles/boutons compacts)**
   - Certaines zones cliquables semblent proches de 32–36 px.
   - Recommandé : viser **44x44 px mini**.

### Important (P2)

4. **Lisibilité perfectible sur textes secondaires**
   - Taille fréquente à 12–13 px et usage de `muted`.
   - Impact : fatigue visuelle, effort de lecture augmenté.

5. **Usage important de la couleur/état visuel pour le statut**
   - Risque pour daltonisme si l’état n’est pas toujours redondé par texte/icône claire.

6. **Graphiques potentiellement difficiles sans alternative textuelle riche**
   - Les charts sont pratiques, mais non experts ont besoin de conclusions “en clair”.

### Opportunité (P3)

7. **Langage parfois orienté “métier/tech”**
   - Quelques intitulés peuvent être simplifiés (“imputées”, “mobilisable”, etc.).

8. **Homogénéité à renforcer entre écrans**
   - Même intention UX, mais densité variable selon modules.

## 4) Recommandations concrètes

## Lot A — Quick wins (1 à 2 jours)

1. **Ajouter un lien d’évitement clavier** en haut de page : “Aller au contenu principal”.
2. **Augmenter la taille de base** (ex. 16px min) et porter les textes secondaires à 14px mini.
3. **Fixer des cibles interactives min 44x44 px** (pastilles nav, boutons, icônes de fermeture).
4. **Renforcer l’état focus clavier** (visible partout, contraste élevé, pas seulement couleur légère).
5. **Ajouter un résumé textuel systématique sous chaque graphique** : “Ce qu’il faut retenir”.

## Lot B — Simplicité d’usage (3 à 5 jours)

6. **Réorganiser la topbar en 5 rubriques max** + menu “Plus” stable.
7. **Introduire un mode “Essentiel” global** (pas seulement dashboard), activable dans le profil.
8. **Normaliser les pages formulaires** :
   - ordre de lecture identique,
   - aide contextuelle courte,
   - erreurs au-dessus du formulaire + près du champ.
9. **Uniformiser le vocabulaire en “français simple”** (microcopy inclusive).

## Lot C — Accessibilité durable (1 sprint)

10. **Passer un audit outillé** (axe/Lighthouse + tests clavier + NVDA/VoiceOver).
11. **Mettre en place une checklist QA accessibilité** dans chaque PR (contraste, focus, labels, clavier, zoom 200%).
12. **Créer un “design token” accessibilité** (tailles min, contrastes min, espacements, focus ring standard).

## 5) Grille de simplicité pour publics non experts

- Se repérer rapidement : **2.5/5**
- Comprendre quoi faire ensuite : **3/5**
- Éviter les erreurs : **3/5**
- Corriger une erreur facilement : **3/5**
- Confort de lecture : **2.5/5**
- Accessibilité visuelle (thèmes, contrastes, zoom, focus) : **3/5**

**Score global simplicité perçue : 2.8 / 5**

## 6) Plan priorisé recommandé

1. **Semaine 1** : skip link + focus + tailles + cibles 44px + résumés textuels charts.
2. **Semaine 2** : simplification topbar + mode Essentiel global.
3. **Semaine 3** : harmonisation formulaires + dictionnaire de microcopies.
4. **Semaine 4** : audit outillé + correction écarts AA prioritaires.

## 7) Indicateurs de succès à suivre

- Taux d’abandon sur formulaires clés.
- Temps moyen “première action utile” après connexion.
- Nombre de tickets support “je ne trouve pas / je ne comprends pas”.
- Taux de réussite au clavier uniquement (scénarios critiques).
- Résultat Lighthouse Accessibility et nombre d’écarts WCAG ouverts/fermés.

---

Si tu veux, je peux enchaîner avec un **plan de corrections ultra concret écran par écran** (connexion, dashboard, participants, ateliers), avec estimation en jours et ordre d’implémentation.
