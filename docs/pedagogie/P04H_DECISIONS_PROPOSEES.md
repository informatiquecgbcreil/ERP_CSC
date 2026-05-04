# P0.4H — Décisions proposées

## Décision 1 — Source de vérité

La source de vérité des observations individuelles devient :

```text
Evaluation
```

Parce qu’elle contient déjà :

```text
participant_id
competence_id
session_id
etat
commentaire
date_evaluation
user_id
```

## Décision 2 — Nom utilisateur

Ne pas dire “compétence” partout.

Dire :

```text
Savoir-faire observé
```

## Décision 3 — Séance ↔ savoir-faire

Utiliser la relation existante :

```text
SessionActivite.competences
```

via la table :

```text
session_competence
```

## Décision 4 — Objectif ↔ savoir-faire

Utiliser la relation existante :

```text
Objectif.competences
```

via la table :

```text
objectif_competence
```

## Décision 5 — ObjectifSuivi

Ne plus l’utiliser comme source principale.

Le garder en compatibilité / historique.

## Décision 6 — SessionAssessmentSkill

Ne pas l’utiliser pour le suivi individuel P0.4I.

Elle n’est pas rattachée directement à un participant.

## Décision 7 — DigComp

Reporter.

DigComp viendra plus tard via les tables `Skill` / `Framework`, ou par un mapping vers `Competence`.

## Décision 8 — Prochaine implémentation

Créer :

```text
/pedagogie/seance/<session_id>
```

Avec :

```text
savoir-faire observés
participants présents
grille d’observation
sauvegarde dans Evaluation
```
