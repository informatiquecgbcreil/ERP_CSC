# P0.4H — Audit du modèle séance / référentiel / observations

Base analysée : `AppGestion.zip`  
Base de travail déclarée : **30/04/2026 à 16h43**  
Généré le : `2026-05-01T18:40:19`

## 1. Verdict

Le modèle métier cible est maintenant clair :

```text
Séance
→ objectif de séance
→ items du référentiel observés
→ observations individuelles
→ passeport individuel
→ indicateurs de séance
→ objectifs opérationnels / spécifiques / généraux
```

L’application possède déjà une base assez intéressante, mais il faut arrêter de faire cohabiter plusieurs systèmes d’évaluation.

Le point important de l’audit : **la table `Evaluation` est la meilleure candidate comme source de vérité des observations individuelles**, parce qu’elle contient déjà :

```text
participant_id
competence_id
session_id
user_id
etat
date_evaluation
commentaire
```

Donc elle correspond très bien à :

```text
participant + séance + item de référentiel + niveau observé + commentaire
```

## 2. Ce qui existe déjà

### `SessionActivite`

Colonnes détectées :

```text
id, atelier_id, secteur, session_type, date_session, heure_debut, heure_fin, capacite, statut, rdv_date, rdv_debut, rdv_fin, duree_minutes, created_at, consommation_config_id, is_deleted, deleted_at, kiosk_open, kiosk_pin, kiosk_token, kiosk_opened_at
```

La séance existe déjà et possède déjà une relation `competences` via la table d’association `session_competence`.

Conclusion :

```text
SessionActivite peut déjà être reliée à des items de référentiel.
```

Mais elle ne porte pas encore clairement :

```text
objectif de séance
bilan qualitatif animateur
pertinence / difficulté / commentaire pédagogique
```

### `PresenceActivite`

Colonnes détectées :

```text
id, session_id, participant_id, motif, motif_autre, signature_path, created_at
```

C’est la base pour générer la grille d’observation :

```text
participants présents × items observés dans la séance
```

### `Competence`

Colonnes détectées :

```text
id, referentiel_id, code, nom, description
```

C’est le meilleur nom technique actuel pour ce qu’on appellera côté utilisateur :

```text
Savoir-faire observé
```

### `Evaluation`

Colonnes détectées :

```text
id, participant_id, competence_id, session_id, user_id, etat, date_evaluation, commentaire
```

C’est la meilleure source de vérité future.

Elle a déjà une contrainte d’unicité :

```text
participant_id + competence_id + session_id
```

Donc pour une même séance, un participant ne peut avoir qu’une seule observation par item. C’est exactement ce qu’il faut.

### `Objectif`

Colonnes détectées :

```text
id, parent_id, type, titre, description, seuil_validation, projet_id, atelier_id, session_id, module_id, created_at
```

`Objectif` garde un rôle utile pour la hiérarchie :

```text
général → spécifique → opérationnel
```

Il possède aussi une relation `competences`. Donc un objectif peut être relié à plusieurs items de référentiel.

Conclusion :

```text
Les observations Evaluation → Competence peuvent remonter vers Objectif via objectif_competence.
```

### `ObjectifSuivi`

Colonnes détectées :

```text
id, objectif_id, session_id, participant_id, mode, etat, ressenti, commentaire, date_saisie, user_id, created_at, updated_at
```

Cette table est encore utilisée par le kiosk actuel. Mais elle est centrée sur `objectif_id`, pas sur `competence_id`.

Conclusion :

```text
ObjectifSuivi doit devenir historique / compatibilité.
Evaluation doit devenir la source structurée.
```

### `SessionSkill`, `SessionAssessment`, `SessionAssessmentSkill`

Colonnes détectées :

```text
SessionSkill : session_id, skill_id, expected_level, coverage, created_at

SessionAssessment : id, session_id, project_id, method, notes, assessed_at, assessed_by_id

SessionAssessmentSkill : id, session_assessment_id, skill_id, result, score, observed_level, comment, created_at
```

Ces tables utilisent plutôt `Skill`, pas `Competence`, et `SessionAssessmentSkill` n’a pas de `participant_id`.

Conclusion :

```text
Elles ne sont pas idéales pour le suivi individualisé actuel.
Elles peuvent rester pour une future couche DigComp / Skill, mais pas pour P0.4I.
```

## 3. Décision recommandée

### Source de vérité

Utiliser :

```text
Evaluation
```

comme source de vérité des observations individuelles.

Traduction métier :

```text
Pour chaque participant présent,
sur chaque savoir-faire observé dans la séance,
on stocke un niveau et un commentaire.
```

### Liaison séance ↔ items observés

Utiliser l’association existante :

```text
session_competence
```

via :

```text
SessionActivite.competences
```

C’est plus propre que de créer une nouvelle table.

### Liaison item ↔ objectifs

Utiliser l’association existante :

```text
objectif_competence
```

via :

```text
Objectif.competences
```

Cela permet :

```text
Evaluation
→ Competence
→ Objectif opérationnel
→ Objectif spécifique
→ Objectif général
```

### Objectif de séance

Il manque un stockage propre.

Deux options :

1. ajouter des colonnes à `SessionActivite` ;
2. créer une table `SessionPedagogique`.

Pour une solution propre, je recommande une petite migration plus tard :

```text
session_activite.objectif_seance
session_activite.bilan_qualitatif
session_activite.pertinence
session_activite.difficulte
session_activite.commentaire_pedagogique
```

Mais on peut commencer sans migration avec un premier écran qui utilise les relations déjà existantes.

## 4. Rôle du référentiel

Le référentiel est utile, mais comme **banque d’items observables**.

Langage utilisateur :

```text
Savoir-faire observés
```

Langage technique :

```text
Competence
```

Exemple :

```text
Séance : envoyer un mail avec pièce jointe

Savoir-faire observés :
- ouvrir une boîte mail
- rédiger un message simple
- joindre un fichier
- envoyer le message
```

## 5. Rôle des objectifs

Les objectifs ne doivent pas être la grille d’évaluation quotidienne.

Ils servent à répondre à :

```text
À quoi cette séance contribue-t-elle dans le projet ?
```

Une séance peut nourrir plusieurs objectifs opérationnels.  
Un savoir-faire peut nourrir plusieurs objectifs.  
Un objectif peut être nourri par plusieurs séances.

## 6. Rôle du passeport

Le passeport doit devenir une lecture individuelle des `Evaluation`.

Pas de double saisie.

```text
Evaluation
→ fiche participant / passeport
```

## 7. Ce qu’il faut éviter

Ne pas continuer à écrire les observations principales dans :

```text
ObjectifSuivi
```

sinon les résultats seront coupés entre deux mondes.

Ne pas utiliser `SessionAssessmentSkill` pour P0.4I, car il n’est pas individualisé par participant dans le modèle actuel.

Ne pas brancher DigComp tout de suite. Les tables `Skill` peuvent attendre.

## 8. Suite logique

### P0.4I — Écran séance complète, version minimale

Créer une page :

```text
/pedagogie/seance/<session_id>
```

Elle doit permettre :

```text
1. choisir les savoir-faire observés pendant la séance ;
2. afficher les participants présents ;
3. saisir une observation individuelle par participant et par savoir-faire ;
4. écrire dans Evaluation ;
5. garder ObjectifSuivi en compatibilité ancienne, mais ne plus l’utiliser comme cœur.
```

### P0.4J — Objectif de séance + bilan qualitatif

Avec migration légère sur `SessionActivite`.

### P0.4K — Passeport apprentissages

Lire `Evaluation` par participant.

### P0.4L — Indicateurs d’objectifs

Calculer :

```text
Evaluation → Competence → Objectif
```

## 9. Conclusion

Le squelette propre est :

```text
SessionActivite
→ session_competence
→ Competence
→ Evaluation
→ passeport / objectifs / bilans
```

Donc on peut avancer sans créer une nouvelle usine à gaz.
