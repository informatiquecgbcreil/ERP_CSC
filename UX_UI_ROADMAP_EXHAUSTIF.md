# Roadmap UX / UI exhaustive (priorisée) — Application Avril

> Objectif: améliorer l'expérience utilisateur sur **chaque écran existant**, avec gestion fine des rôles, aides visuelles, logique d'usage et automatisations, tout en gardant une architecture évolutive.

## 1) Priorités globales transverses

### P0 — À faire en premier (fort impact, faible risque)
1. **Uniformiser le niveau d'information selon le rôle** sur toutes les pages (Direction/Finance/Admin tech/Responsable secteur), avec:
   - bloc "Pourquoi je vois ça";
   - badge "Portée" (Tous secteurs / Secteur assigné);
   - actions non autorisées masquées (pas seulement désactivées).
2. **Système d'aide contextuelle standard** (tooltip + callout + "Que faire ensuite ?") en haut de chaque écran métier.
3. **Filtrage persistant** (query params + localStorage par page) avec bouton "Réinitialiser".
4. **Actions critiques sécurisées**: double confirmation + impact preview (suppression, anonymisation, purge, clôture).
5. **États vides pédagogiques**: proposer l'action suivante au lieu d'une liste vide.
6. **Feedback de traitement unifié**: toasts, pending states sur boutons, erreurs regroupées en haut de formulaire.
7. **Design tokens / composants communs**: boutons, cards, tables, formulaires, statuts, tags (réduction dette UI).

### P1 — Deuxième lot (amélioration usage quotidien)
8. **Vues “résumé + détail” systématiques**: KPI synthèse en haut + table actionnable en dessous.
9. **Sauvegarde auto-brouillon** pour formulaires longs (bilan, objectifs, subvention, questionnaire).
10. **Auto-complétion intelligente** (ville/quartier, financeur, libellés récurrents, motifs).
11. **Raccourcis clavier** sur écrans volumineux (recherche, création, sauvegarde).
12. **Historique des modifications** visible (qui, quoi, quand) sur écrans sensibles.

### P2 — Scalabilité produit
13. **Moteur de vues configurables** (colonnes, tri, filtres enregistrés par profil).
14. **Workflow “état” standard** (brouillon / validé / archivé) sur entités clés.
15. **Notifications internes** (anomalies budget, sessions sans émargement, relances questionnaire).
16. **Audit UX analytics** (temps de tâche, points d'abandon, erreurs fréquentes).

---

## 2) Recommandations par page (exhaustif)

## A. Authentification & entrée

### `/` — Login
- Ajouter **affichage clair du contexte d'instance** (nom structure, environnement) pour éviter les erreurs de connexion inter-sites.
- Pré-remplir dernier email utilisé (option locale) + afficher Caps Lock détecté.
- Message d'erreur plus actionnable (email introuvable vs mot de passe incorrect côté UX, sans fuite sécurité côté backend).
- Lien direct vers "mot de passe oublié" plus visible.

### `/password-reset` — Demande de réinitialisation
- Ajouter indicateur de délai d'envoi attendu + mention anti-spam.
- Afficher source de lien (email / lien debug en dev) de manière explicite.

### `/password-reset/<token>` — Nouveau mot de passe
- Barre de robustesse + check-list policy (longueur, complexité).
- Visibilité du mot de passe (icône œil) + compteur caractères.

### `/setup` — Assistant initial
- Transformer en **wizard à étapes** avec progression (1/4, 2/4...).
- Validation inline (SMTP testable avant fin).
- Génération automatique d'un utilisateur test lecture seule (optionnel).

### `/launcher` — Portail QR
- Ajouter bouton "copier URL" et état de copie.
- Explication "quand utiliser QR kiosque vs admin" en 1 phrase.
- QR fallback texte large pour impression.

---

## B. Navigation globale / shell

### `base.html` (topbar + navigation)
- Remplacer la barre en "pills" par **navigation par domaines** (Finance, Activité, Pédagogie, Admin) + méga-menu.
- Ajouter **fil d'Ariane** sous topbar.
- Ajouter **recherche globale** (participants, projet, subvention, session).
- Ajouter mode "focus" (masquer navigation secondaire sur saisie intense).

---

## C. Dashboard & pilotage global

### `/dashboard`
- Cartes KPI personnalisées par rôle (admin tech: santé système; finance: budget; responsable: activité secteur).
- Alertes classées par criticité + bouton "résoudre" menant à l'écran exact.
- Ajout d'une section "Actions recommandées aujourd'hui" (auto-priorisée).
- Ajouter comparatif période N vs N-1 natif.

### `/stats`, `/stats-bilans`, `/bilan`, `/bilan-global`, `/subvention/<id>/bilan`
- Harmoniser filtres (même composants partout).
- Rendre les graphiques "cliquables" avec drill-down explicite.
- Ajouter export guidé (CSV/XLSX/PDF + description de l'usage).
- Ajouter indicateurs de qualité de données (champs manquants, anomalies).

### `/controle`, `/setup-start`, `/rbac-test`
- Réserver ces écrans au personnel habilité avec encart "outil technique".
- Fournir diagnostic actionnable (problème détecté → action recommandée).

---

## D. Subventions / Budget / Dépenses

### `/subventions`
- Vue duale: "portefeuille" (cards) + "table compacte".
- Créer subvention en modal guidée (templates financeur, exercice, secteur).
- Ajouter score de complétude par dossier (montants, ventilation, liens projets).

### `/subvention/<id>/pilotage` (`budget_pilotage.html`)
- Segmenter en tabs: Aperçu / Lignes / Dépenses / Projets liés / Historique.
- Automatiser propositions de ventilation avec simulation avant application.
- Afficher garde-fous visuels (dépassement, incohérences) sur chaque ligne.
- Ajout "clôturer l'exercice" avec checklist.

### `/depenses`, `/depense/nouvelle`, `/depense/<id>/edit`
- Création en 2 temps: "Informations essentielles" puis "imputation et pièces".
- OCR basique des justificatifs (montant/date/fournisseur pré-remplis) pour accélérer saisie.
- Validation métier en direct (date hors période, montant négatif, ligne incompatible).
- Historique des pièces et versionning document.

---

## E. Projets & budget projet

### `/projets`, `/projets/new`, `/projets/<id>`
- Dashboard projet: objectifs, budget, partenaires, sessions liées, risques.
- Timeline projet avec jalons et statuts.
- Check-list "projet prêt à déposer" / "projet à suivre".

### `/projets/<id>/budget/*` (charges, produits, ventilation, synthèse)
- Mode feuille de calcul ergonomique (édition rapide clavier).
- Contrôle de cohérence inter-onglets (totaux sync en temps réel).
- Bloc "écart prévisionnel vs réalisé" + recommandations automatiques.
- Export contextuel par onglet.

---

## F. Participants

### `/participants`
- Séparer clairement "annuaire global" vs "participants du secteur".
- Afficher règles de visibilité selon rôle (pour réduire incompréhension).
- Filtres avancés enregistrables (vues favorites: actifs, à relancer, doublons potentiels).
- Ajout colonne "dernière activité" + statut actif/inactif.

### `/participants/new`, `/participants/<id>/edit`
- Formulaire progressif (identité, contact, socio-démo, consentements).
- Aides de qualité de données (email/phone/date format).
- Auto-suggestion quartier depuis ville.

### `/participants/duplicates`
- Workflow de fusion guidé avec aperçu "avant/après".
- Règles de matching explicables et réglables.

---

## G. Activité / ateliers / sessions / émargement

### `/activite/` (index)
- Vue "prochaines sessions" + actions immédiates (ouvrir kiosque, émargement, relance).
- Statuts explicites: session brouillon/ouverte/fermée/archivée.

### `/activite/participants`, `/activite/participant/<id>/edit`
- Limiter redondance avec module Participants via composants partagés.
- Bouton "ouvrir fiche complète participant".

### `/activite/atelier/new`, `/activite/atelier/<id>/edit`, `/activite/atelier/<id>/sessions`
- Assistant de création atelier (périodicité, capacité, objectifs).
- Visualiser charge/capacité mensuelle directement.

### `/activite/atelier/<id>/session/new`, `/session/<id>/edit-schedule`
- Création de session rapide à partir de modèles.
- Vérification conflits planning ressources/animateurs.

### `/session/<id>/skills`, `/session/<id>/evaluation_batch`
- Matrice compétences plus lisible (tri par niveau, code couleur).
- Évaluation batch avec raccourcis clavier et autosave.

### `/session/<id>/emargement`
- Mode terrain mobile-first, boutons larges, saisie ultra rapide.
- Alerte immédiate sur doublon de présence/jour.
- Génération documents et emailing regroupés dans un panneau "Clôture session".

---

## H. Kiosk public

### `/kiosk/`
- UX ultra simplifiée: saisie code plein écran + gros CTA.
- Accessibilité renforcée (contraste, clavier tactile, feedback erreur clair).

### `/kiosk/session/<token>`
- Parcours en étapes visuelles: Rechercher → Choisir → Signer → Confirmation.
- Signature optimisée tactile (anti-scroll, bouton effacer visible).
- Création participant "express" avec minimum légal, puis enrichissement ultérieur côté staff.

### `/kiosk/session/<token>/feedback`
- Questionnaires en mode "1 question / écran" (meilleur taux de complétion).
- Indicateur progression + temps estimé.
- Message de fin personnalisé (et anonymat explicitement expliqué).

---

## I. Pédagogie

### `/referentiels`, `/referentiels/<id>`
- Arborescence compétences avec recherche instantanée.
- Import CSV avec prévisualisation et mapping assisté.

### `/modules`, `/objectifs`, `/plan_projet`
- Liens visuels objectifs↔modules↔projets (graphe simple).
- Détection automatique des objectifs orphelins/non mesurables.

### `/suivi`, `/stats/pedagogie`, `/stats/pedagogie/participant/<id>/bilan`
- Vue "progression" par participant et par groupe.
- Alertes pédagogiques (participant décrocheur, compétence stagnante).

### `/pedagogie/kiosk`
- Paramétrage guidé des questions et de la posture animateur (scripts recommandés).

### `/participant/<id>/passeport`, `/pilotage`
- Passeport structuré en sections (compétences, preuves, commentaires, plan d'action).
- Génération automatique de synthèse narrative à partir des évaluations.

---

## J. Bilans

### `/bilans`, `/bilans/secteur`, `/bilans/subvention`, `/bilans/qualite`, `/bilans/inventaire`
- Modèle narratif assisté: "faits", "preuves", "résultats", "suite".
- Indication de complétude documentaire (pièces manquantes).

### `/bilans/lourds`
- Éditeur long-form avec autosave + sommaire latéral.
- Upload médias simplifié (drag-drop, compression auto).
- Export DOCX paramétrable (financeur, période, périmètre).

---

## K. Inventaire & factures

### `/inventaire` (factures), `/inventaire/nouvelle`, `/inventaire/<id>`
- Pipeline facture: reçue → vérifiée → validée → imputée.
- Suggestions automatiques d'imputation via historique.

### `/inventaire-materiel/`, `/new`, `/<id>`
- Cycle de vie matériel (en stock, affecté, en panne, sorti).
- Lien bidirectionnel avec dépense/facture d'origine.
- QR code par équipement pour consultation terrain.

---

## L. Quartiers & partenaires

### `/quartiers`, `/quartiers/<id>/edit`, `/quartiers/stats`
- Aide cartographique et normalisation des noms.
- Indicateurs d'activité par quartier + tendance.

### `/partenaires`, `/partenaires/new`, `/partenaires/<id>/edit`
- CRM léger: interactions, échéances, niveau d'engagement.
- Relances automatiques (partenaires inactifs depuis X jours).

---

## M. Questionnaires

### `/questionnaires`, `/new`, `/<id>/edit`
- Builder de questionnaire avec templates (satisfaction, sortie atelier, impact).
- Aperçu live participant.

### `/questionnaires/session/<id>`
- Collecte simplifiée animateur + mode saisie rapide après atelier.
- Détection des réponses partielles et relance douce.

---

## N. Administration

### `/admin/users`
- Onboarding utilisateur guidé (rôle + secteur + permissions dérivées).
- Afficher "ce que cet utilisateur verra" avant validation.

### `/admin/droits`
- Matrice permissions lisible par domaine avec recherche.
- Simulateur "impersonation" en lecture seule.

### `/admin/secteurs`
- Fusion secteur (avec migration assistée des données).
- Avertissement d'impact avant désactivation.

### `/admin/instance`
- Check de santé instance (smtp, storage, base URL, sauvegarde).
- Journal des changements de configuration.

### `/admin/import-excel`, `/admin/referentiels`, `/admin/referentiels/import`
- Import wizard avec étapes: fichier → mapping → validation → exécution.
- Rapport d'import téléchargeable, erreurs regroupées par catégorie.

### `/admin/import-skills`
- Gestion de versions de référentiel + rollback.

### `/admin/debug_rbac`
- Réserver clairement au debug, avec bannière environnement.

---

## 3) Informations à afficher selon les rôles (synthèse d'implémentation)

1. **Direction/Finance**: visibilité globale multisecteur + consolidations + alertes stratégiques.
2. **Responsable secteur**: prioriser les écrans opérationnels de son secteur + comparatifs locaux.
3. **Admin technique**: cacher bruit métier, montrer santé système, droits, imports, instance.
4. **Animateur/kiosk**: interface ultra simple centrée présence/feedback, sans éléments administratifs.

Implémentation UX recommandée:
- badge de rôle + badge de portée dans l'en-tête de page;
- composants de page conditionnels par permission;
- traces d'audit des actions sensibles visibles aux rôles habilités.

---

## 4) Automatisations prioritaires

1. Suggestions d'imputation dépense ↔ ligne budget.
2. Pré-remplissage participant depuis historique récent.
3. Alertes proactives (dépassement budget, session sans émargement, questionnaire non rempli).
4. Relances partenaires et tâches de clôture mensuelle.
5. Génération assistée de synthèses bilans et pédagogie.
6. Contrôles de cohérence nocturnes + rapport matinal.

---

## 5) Stratégie d'évolutivité (future-proof)

1. **Design system interne**: composants versionnés + documentation storybook-like.
2. **Feature flags** par module/instance.
3. **Schéma de permissions stable** (codes immuables + labels évolutifs).
4. **Instrumentation produit** (event tracking privacy-by-design).
5. **Contrats API/UI**: sérialiseurs standard, payloads versionnés.
6. **Système de templates configurables** pour bilans/questionnaires/exports.

---

## 6) Plan d'exécution recommandé

- **Sprint 1 (P0)**: navigation/rôles/aides/filtres persistants/actions critiques.
- **Sprint 2 (P1)**: formulaires intelligents/autosave/historique/raccourcis.
- **Sprint 3 (P1-P2)**: automatisations métier + workflows d'état.
- **Sprint 4 (P2)**: instrumentation et personnalisation avancée des vues.

