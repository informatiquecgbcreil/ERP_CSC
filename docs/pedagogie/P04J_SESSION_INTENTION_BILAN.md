# P0.4J — Intention et bilan qualitatif portés par la séance

## Problème

L’intention de séance ne doit pas être stockée comme un `Objectif`.

Sinon, chaque séance crée un nouvel objectif et le listing devient ingérable.

## Correction

L’intention et le bilan qualitatif sont portés par `session_activite`.

Nouveaux champs :

```text
intention_seance
intention_seance_detail
bilan_qualitatif
pertinence
difficulte
participation_groupe
a_reprendre
commentaire_pedagogique
```

## Chaîne métier

```text
Objectif général
→ objectif spécifique
→ objectif opérationnel
→ intention de séance
→ savoir-faire observés
→ observations individuelles
```

## Migration

```text
34f5a6b7c8d9_session_pedagogical_fields.py
```

Elle copie les anciennes intentions créées comme `Objectif.session_id` vers les nouveaux champs de séance, sans supprimer automatiquement les anciens objectifs.
