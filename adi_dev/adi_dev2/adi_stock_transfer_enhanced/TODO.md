# ADI Stock Transfer Enhanced - Suivi du Développement

## Date: 28/12/2025

---

## FONCTIONNALITÉS IMPLÉMENTÉES

### 1. Réservation Multi-Source
- [x] Champ `use_multi_source` (Boolean) - activé par défaut
- [x] Champ `source_location_order` (Selection) - ordre alphabétique par défaut
- [x] Calcul de disponibilité incluant les sous-emplacements
- [x] Appel automatique de `action_assign()` à l'approbation
- [x] Validation : bloque si quantité totale insuffisante (pas de partiel)

### 2. Traçabilité des Sources
- [x] Nouveau modèle `adi.stock.transfer.line.source`
- [x] Enregistrement automatique de la répartition après réservation
- [x] Champs : location_id, quantity_reserved, quantity_done, move_line_id

### 3. Interface Utilisateur
- [x] Onglet "Répartition Sources" dans le formulaire transfert
- [x] Colonnes "Nb Sources" et "Répartition" dans les lignes
- [x] Bouton statistique "Sources"
- [x] Alerte informative mode multi-source
- [x] Filtres recherche : Multi-Source / Mode Legacy

### 4. Correction Bug Envoi
- [x] Surcharge `action_start_transit()` pour travailler avec move_lines
- [x] Gestion correcte de `qty_done` sur les `stock.move.line`

---

## PROCHAINE FONCTIONNALITÉ À IMPLÉMENTER

### Restriction de Réception au Responsable Destination

#### Objectif
Empêcher le demandeur de valider la réception. Seul le responsable
destination (ou Manager) peut confirmer la réception.

#### Éléments à Créer

1. **Configuration (res.config.settings)**
   ```python
   restrict_reception_to_dest_responsible = fields.Boolean(
       "Restreindre la réception au responsable destination",
       config_parameter='adi_stock_transfer_enhanced.restrict_reception'
   )
   ```

2. **Modification du Transfert**
   - Utiliser le champ existant `dest_responsible_id`
   - Le rendre obligatoire SI la configuration est activée
   - Ajouter contrainte sur `action_done()`:
     - Vérifier si config activée
     - Si oui: seul dest_responsible_id OU Manager peut terminer
     - Sinon: comportement actuel

3. **Activités Automatiques**

   À l'ENVOI (action_start_transit):
   ```python
   # Créer activité pour le responsable destination
   self.activity_schedule(
       'mail.mail_activity_data_todo',
       user_id=self.dest_responsible_id.id,
       summary="Réception transfert à confirmer",
       note=f"Le transfert {self.name} est en route vers votre dépôt."
   )
   ```

   À la RÉCEPTION (action_done_confirmed):
   ```python
   # Marquer l'activité comme faite
   self.activity_feedback(['mail.mail_activity_data_todo'])

   # Créer activité pour informer le demandeur
   self.activity_schedule(
       'mail.mail_activity_data_todo',
       user_id=self.requester_id.id,
       summary="Transfert réceptionné",
       note=f"Le transfert {self.name} a été réceptionné par {self.env.user.name}"
   )
   ```

4. **Vue Configuration**
   - Ajouter dans les paramètres Inventaire ou créer menu dédié
   - Checkbox pour activer/désactiver la restriction

5. **Modification Vue Formulaire**
   - Rendre `dest_responsible_id` visible et obligatoire si config activée
   - Masquer bouton "Terminer" si user != dest_responsible_id et != Manager

#### Fichiers à Modifier/Créer
- [ ] `models/res_config_settings.py` (nouveau)
- [ ] `models/stock_transfer.py` (modifier action_done, action_start_transit)
- [ ] `views/res_config_settings_views.xml` (nouveau)
- [ ] `views/stock_transfer_views.xml` (ajouter champ dest_responsible_id)
- [ ] `__manifest__.py` (ajouter les nouveaux fichiers data)
- [ ] `models/__init__.py` (importer res_config_settings)

#### Questions Résolues
- [x] Utiliser champ existant `dest_responsible_id` → OUI
- [x] Qui définit le responsable → Le demandeur (ou validateur)
- [x] Manager peut outrepasser → OUI
- [x] Notifications → OUI via activités

---

## STRUCTURE ACTUELLE DU MODULE

```
adi_stock_transfer_enhanced/
├── __init__.py
├── __manifest__.py
├── TODO.md                          ← CE FICHIER
├── models/
│   ├── __init__.py
│   ├── stock_transfer.py            # Extension transfert
│   ├── stock_transfer_line.py       # Extension lignes
│   └── stock_transfer_line_source.py # Nouveau modèle sources
├── views/
│   └── stock_transfer_views.xml     # Vues héritées
└── security/
    └── ir.model.access.csv          # Droits d'accès
```

---

## COMMANDES UTILES

```bash
# Mettre à jour le module
cd /home/stadev/odoo15-dev
./odoo-bin -d o15_ab_latest --addons-path=addons,odoo/addons,adi_dev/adi_dev2 \
    --stop-after-init -u adi_stock_transfer_enhanced

# Vérifier la syntaxe
cd /home/stadev/odoo15-dev/adi_dev/adi_dev2/adi_stock_transfer_enhanced
python3 -m py_compile models/*.py
python3 -c "import xml.etree.ElementTree as ET; ET.parse('views/stock_transfer_views.xml')"

# Requête base de données
psql -d o15_ab_latest -c "SELECT * FROM adi_stock_transfer WHERE name = 'TRANS/2025/00046';"
```

---

## NOTES IMPORTANTES

1. **Redémarrage serveur requis** après chaque mise à jour du module
2. **Champ `dest_responsible_id` existe déjà** dans la table (vérifié en base)
3. **Transferts existants** ont `use_multi_source = True` par défaut
4. **Base de test** : o15_ab_latest

---

Bonne continuation !
