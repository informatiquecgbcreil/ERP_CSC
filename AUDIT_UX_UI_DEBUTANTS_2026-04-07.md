# Audit UX/UI exhaustif — focus utilisateurs débutants / non experts

_Date : 7 avril 2026_

## 1) Synthèse exécutive

L’application est déjà riche et couvre beaucoup de cas métier, mais elle reste **dense cognitivement** pour un public débutant. Les points de friction majeurs ne viennent pas d’un manque de fonctionnalités, mais surtout de :

1. **Navigation et orientation** : l’utilisateur ne sait pas toujours « où il est » ni « quoi faire ensuite ».
2. **Charge mentale sur les formulaires** : trop d’informations en une fois, hiérarchie des champs perfectible.
3. **Feedback d’action inégal** : confirmations, statuts et messages de succès/erreur pas toujours homogènes.
4. **Parcours terrain (émargement/kiosque)** : puissant mais encore trop « expert » dans la présentation.

L’axe recommandé est donc : **“moins d’hésitation, plus de guidage”** plutôt que “ajouter de nouveaux écrans”.

---

## 2) Ce qui fonctionne déjà bien

- Les écrans clés utilisent déjà des éléments utiles aux débutants : KPI, aides textuelles, états vides pédagogiques, boutons d’action explicites.
- Présence d’un socle de design (boutons, cartes, formulaires) et de helpers UX réutilisables.
- Des sections importantes montrent déjà une intention de pédagogie (ex. « Flux conseillé » en émargement).

---

## 3) Frictions UX/UI prioritaires (avec impact direct sur le temps utilisateur)

## A. Orientation globale et compréhension du contexte

### Constats
- La navigation principale par « pills » reste lisible, mais n’exprime pas clairement la logique métier par domaine pour un débutant.
- L’utilisateur voit des actions nombreuses sans priorisation claire de la prochaine étape.
- Le contexte de rôle/périmètre n’est pas toujours suffisamment explicite en continu.

### Améliorations à faible coût
1. Ajouter un **fil d’Ariane standard** sous le header sur les écrans de gestion.
2. Ajouter un mini bloc « **Prochaine action recommandée** » en haut de chaque écran dense.
3. Ajouter une puce fixe « **Vous êtes en mode : [rôle] / [périmètre]** » dans l’en-tête des pages sensibles.

### Gain attendu
- Diminution des erreurs de navigation et du temps de recherche d’action (surtout 1ers jours d’usage).

---

## B. Login et entrée dans l’outil

### Constats
- L’écran de connexion est clair, mais minimal pour les besoins réels d’un public non expert.
- Pas d’aide immédiate sur erreurs classiques (Caps Lock, confusion email pro/perso, etc.).

### Améliorations à faible coût
1. Préremplir le dernier email saisi localement.
2. Ajouter un indicateur visuel simple de verrouillage majuscule.
3. Afficher une formulation d’erreur orientée action (« Vérifiez votre email professionnel »).

### Gain attendu
- Moins d’échecs de connexion et moins de sollicitations support.

---

## C. Liste participants : rapidité de tri et lisibilité

### Constats
- L’écran est globalement bien structuré (filtres + KPI + tableau), mais peut être lourd au premier abord.
- Les filtres sont nombreux ; le novice hésite sur la combinaison utile.
- Les actions ligne par ligne sont correctes, mais le signal d’urgence/prochaines actions est faible.

### Améliorations à faible coût
1. Ajouter 3 **filtres rapides prédéfinis** (ex. « à recontacter », « sans présence », « nouveaux »).
2. Mettre en avant un mode « **Vue simplifiée** » (moins de colonnes, actions essentielles).
3. Ajouter une colonne « **Dernière activité** » et un badge « inactif > 90 jours ».

### Gain attendu
- Réduction des clics de filtrage et meilleur tri des priorités quotidiennes.

---

## D. Formulaire participant : réduction de la charge cognitive

### Constats
- La fiche est complète, mais tout est affiché en bloc, ce qui intimide un débutant.
- Plusieurs champs utilisent des libellés techniques ou des codes implicites.
- Un défaut visible sur les valeurs de type de public peut créer de la confusion (condition incohérente sur « Bénévole »).

### Améliorations à faible coût
1. Passer en **sections progressives** : Identité → Contact → Localisation → Compléments.
2. Ajouter des exemples de saisie (placeholder orienté usage réel).
3. Ajouter une mini vérification inline (format téléphone/email/date).
4. Corriger l’incohérence de mapping sur le type de public pour éviter les surprises en édition.

### Gain attendu
- Temps de saisie réduit, moins d’erreurs de données et meilleure confiance utilisateur.

---

## E. Émargement : parcours terrain à simplifier

### Constats
- L’écran est très riche (kiosque, modules, présence, évaluation, documents) : très utile, mais dense.
- Pour un animateur débutant, il est difficile de savoir l’ordre optimal des actions.
- L’étape signature est bien présente, mais la signalétique « terminé / à faire » pourrait être plus explicite.

### Améliorations à faible coût
1. Ajouter un **mode guidé en 3 étapes** en haut :
   - 1) Ouvrir le kiosque / préparer session
   - 2) Enregistrer présences
   - 3) Évaluer / clôturer
2. Ajouter des badges d’état sur ces étapes (À faire / En cours / Terminé).
3. Réduire visuellement les sections avancées dans des accordéons « Expert » par défaut fermés.

### Gain attendu
- Meilleure exécution terrain, moins d’oubli (kiosque, validation, évaluation).

---

## F. Feedback système et confirmations

### Constats
- L’application utilise déjà des flashes/messages, mais la cohérence perçue peut être améliorée.
- Les confirmations destructives existent mais sans toujours expliciter l’impact (nombre d’éléments, conséquence).

### Améliorations à faible coût
1. Standardiser les toasts : Succès / Erreur / Info avec structure unique.
2. Ajouter une phrase « **Ce qui vient de se passer** + **prochaine action** » après une opération importante.
3. Sur actions sensibles, afficher une prévisualisation d’impact avant validation finale.

### Gain attendu
- Réduction des erreurs de manipulation et du sentiment d’incertitude.

---

## G. Accessibilité et confort visuel (débutants = souvent hétérogènes en aisance numérique)

### Constats
- La base visuelle est propre, mais certains écrans très denses peuvent fatiguer.
- Le contraste est globalement correct, toutefois la multiplication des blocs sur certains écrans nuit à la priorisation visuelle.

### Améliorations à faible coût
1. Définir une règle stricte « 1 écran = 1 action primaire ». 
2. Harmoniser la taille des boutons principaux (CTA) et leur position.
3. Ajouter un mode densité « confortable » (espacements augmentés) pour les postes d’accueil.

### Gain attendu
- Moins de fatigue visuelle et moins d’erreurs de clic.

---

## 4) Plan d’action recommandé (sans surcharge fonctionnelle)

## Sprint 1 (impact maximal, faible risque)
1. Fil d’Ariane + bloc « prochaine action » sur 5 écrans majeurs.
2. Filtres rapides prédéfinis sur la liste participants.
3. Mode guidé 3 étapes sur émargement.
4. Standardisation du feedback (succès/erreur + prochaine action).

## Sprint 2
1. Formulaire participant en sections progressives.
2. Validation inline légère (email/téléphone/date).
3. Corrections de wording et microcopie orientée débutants.

## Sprint 3
1. Mode vue simplifiée sur écrans denses.
2. Badges d’état uniformes (workflow visuel).
3. Ajustements accessibilité/contraste/densité.

---

## 5) Backlog “gains de temps” ultra pragmatique

1. **Templates de filtres enregistrables** par utilisateur sur listes volumineuses.
2. **Pré-remplissage intelligent** des champs répétitifs (ville, motif, financeur, etc.).
3. **Boutons d’action contextuelle** “Faire ensuite” après chaque sauvegarde.
4. **Raccourcis clavier simples** sur les écrans de saisie fréquente.
5. **Historique minimal** « modifié par / quand » visible là où le doute est fréquent.

---

## 6) Priorisation finale (matrice impact / effort)

### Top 5 à lancer immédiatement
1. Mode guidé d’émargement (impact très fort / effort faible-moyen).
2. Filtres rapides + vue simplifiée participants (impact fort / effort faible).
3. Bloc « prochaine action » transversal (impact fort / effort faible).
4. Standard de feedback post-action (impact fort / effort faible).
5. Segmentation progressive du formulaire participant (impact fort / effort moyen).

Ces cinq actions améliorent fortement l’expérience des non experts sans alourdir le produit : elles **accélèrent l’exécution** plutôt qu’ajouter des fonctionnalités complexes.

---

## 7) Sources observées dans le code (échantillon représentatif)

- Navigation et structure globale : `app/templates/base.html`
- Connexion : `app/templates/login.html`
- Tableau de bord : `app/templates/dashboard.html`
- Liste participants : `app/templates/participants/list.html`
- Formulaire participant : `app/templates/participants/form.html`
- Émargement : `app/templates/activite/emargement.html`
- Styles globaux : `static/style.css`
- Documents UX existants : `UX_UI_ROADMAP_EXHAUSTIF.md`
