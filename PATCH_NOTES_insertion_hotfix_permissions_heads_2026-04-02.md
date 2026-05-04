# Hotfix insertion — permissions fines + Alembic heads

Ce hotfix corrige deux points du patch socle insertion :

1. **Plus de dépendance forte au rôle `charge_insertion`**
   - le module insertion repose désormais sur des **permissions** ;
   - n'importe quel utilisateur peut y accéder si on lui attribue les permissions adaptées ;
   - le menu Insertion n'est plus conditionné à un rôle spécifique.

2. **Boot plus robuste avec Alembic**
   - au démarrage, l'auto-migration utilise maintenant `heads` au lieu de `head` ;
   - cela évite de bloquer le lancement quand plusieurs heads existent dans l'arbre Alembic ;
   - le `stamp` automatique sur base legacy sans `alembic_version` utilise aussi `heads`.

## Fichiers touchés
- `app/__init__.py`
- `app/rbac.py`
- `app/services/insertion.py`
- `app/templates/layout.html`

## Remarque
Si un avertissement **"Revision ... is present more than once"** reste affiché, cela signifie qu'un fichier de migration en double est probablement présent physiquement dans `migrations/versions/`. Le démarrage ne devrait plus être bloqué par le simple cas de plusieurs heads, mais un vrai doublon de fichier reste à nettoyer côté dépôt si besoin.
