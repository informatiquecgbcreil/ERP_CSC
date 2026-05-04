# P0.4I — Écran séance complète

## Objectif

Créer une page claire pour observer les apprentissages pendant une séance.

Nouvelle route principale :

```text
/pedagogie/seance/<session_id>
```

Entrée de liste :

```text
/pedagogie/apprentissages
```

## Source de vérité

Les observations individuelles sont enregistrées dans :

```text
Evaluation
```

Avec la logique :

```text
participant + séance + savoir-faire observé + niveau + commentaire
```

## Tables utilisées

- `SessionActivite` : séance ;
- `PresenceActivite` : participants présents ;
- `SessionActivite.competences` / `session_competence` : savoir-faire observés pendant la séance ;
- `Evaluation` : observations individuelles ;
- `Objectif.competences` / `objectif_competence` : remontée vers objectifs ;
- `Objectif` avec `session_id` : objectif de séance provisoire sans migration.

## Échelle utilisée

```text
Non observé = pas d’Evaluation
0 = En difficulté
1 = En progression
2 = Réussi
3 = Très à l’aise
```

## Limites

Pas encore de migration pour stocker proprement :

```text
objectif_de_seance
bilan_qualitatif
pertinence
difficulte
commentaire_pedagogique
```

Pour l’instant, l’objectif de séance est stocké comme un `Objectif` opérationnel lié à la séance.

## Suite logique

P0.4J :

- migration légère sur `SessionActivite` ;
- vrais champs d’objectif de séance et bilan qualitatif animateur ;
- disparition progressive de `ObjectifSuivi` comme cœur d’évaluation.
