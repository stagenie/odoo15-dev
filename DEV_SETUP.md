# Odoo 15 - Environment de Développement

## Configuration

- **Python**: 3.12.3
- **PostgreSQL**: 16.10
- **Odoo**: 15.0
- **Environnement virtuel**: `/home/stadev/odoo15-dev/venv`

## Structure des dossiers

```
odoo15-dev/
├── odoo/                  # Core Odoo
├── addons/                # Modules Odoo officiels
├── adi_dev/               # Modules personnalisés
├── adi_third_party/       # Modules tiers
├── venv/                  # Environnement virtuel Python
├── odoo-bin               # Script de lancement Odoo
├── odoo.conf              # Configuration Odoo
└── .vscode/               # Configuration VS Code
```

## Démarrer Odoo

### Via ligne de commande

```bash
cd /home/stadev/odoo15-dev
source venv/bin/activate
./odoo-bin -c odoo.conf
```

### Via VS Code

1. Ouvrir le projet dans VS Code: `code /home/stadev/odoo15-dev`
2. Appuyer sur `F5` ou aller dans "Run and Debug"
3. Sélectionner "Odoo 15 - Debug"

## Créer une base de données

```bash
source venv/bin/activate
./odoo-bin -c odoo.conf -d odoo15_dev -i base
```

Ou via l'interface web: http://localhost:8069

## Mettre à jour les modules

```bash
./odoo-bin -c odoo.conf -d odoo15_dev -u nom_du_module
```

## Synchronisation avec GitHub

```bash
# Vérifier le statut
git status

# Ajouter les modifications
git add .

# Commiter
git commit -m "Description des changements"

# Pousser vers GitHub
git push origin main
```

## Extensions VS Code recommandées

Les extensions seront suggérées automatiquement à l'ouverture du projet:
- Python
- Pylance
- XML
- Odoo Snippets
- GitLens

## Logs

Les logs d'Odoo sont dans: `/home/stadev/odoo15-dev/odoo.log`

## Troubleshooting

### Problème de permission PostgreSQL
```bash
psql -l
# Vérifier que l'utilisateur stadev peut créer des DB
```

### Problème de dépendances Python
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Port déjà utilisé
Modifier le port dans `odoo.conf` (ligne `http_port`)
