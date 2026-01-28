# PROJET MAGIMED ISO - Plan d'Implementation et Offre Commerciale

## I. CONTEXTE ET OBJECTIFS

### A. Contexte
**MAGIMED** est active dans le secteur du matériel de conditionnement de produits d'hygiène, pharmaceutiques et médicaux. Pour obtenir la certification ISO, l'entreprise doit mettre en place une traçabilité complète de ses produits sans complexifier ses processus avec un module de gestion de production complet.

### B. Objectifs
1. **Traçabilité complète** via les lots et numéros de série
2. **Gestion simplifiée de la production** via Bons d'Entrée/Sortie
3. **Conformité ISO** avec historique complet des mouvements
4. **Gestion des cautions** sur factures clients

---

## II. ANALYSE DE L'EXISTANT

### A. Base de données actuelle (o15_magimed)
| Element | Valeur |
|---------|--------|
| Produits | 946 (tous sans tracking) |
| Lots | 0 |
| Pickings en cours | 198 |
| Entrepots | 1 (Depot Central) |
| Factures clients | 170 validees |

### B. Modules ADI existants exploitables
- `adi_stock_transfer` - Transferts inter-entrepots
- `adi_stock_transfer_report` - Rapports de transfert
- `adi_inventory_tracking` - Suivi inventaire
- `adi_ab_invoice_reports` - Rapports factures
- `product_inventory_report` - Rapports inventaire

---

## III. ARCHITECTURE DU MODULE adi_magimed

### A. Structure du module

```
adi_magimed/
├── __init__.py
├── __manifest__.py
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   ├── ir_sequence_data.xml
│   ├── stock_picking_type_data.xml
│   └── mail_template_data.xml
├── models/
│   ├── __init__.py
│   ├── product_template.py          # Extension gestion lots
│   ├── stock_production_lot.py      # Extension lots + expiration
│   ├── stock_picking.py             # Extension picking
│   ├── stock_move_line.py           # Saisie lots simplifiee
│   ├── account_move.py              # Gestion cautions
│   └── res_config_settings.py       # Configuration
├── views/
│   ├── menus.xml                    # Menu principal MAGIMED
│   ├── product_template_views.xml
│   ├── stock_production_lot_views.xml
│   ├── stock_picking_views.xml
│   ├── stock_move_history_views.xml
│   ├── account_move_views.xml       # Vue cautions
│   └── expiration_alert_views.xml
├── wizards/
│   ├── __init__.py
│   ├── lot_quick_create_wizard.py
│   ├── stock_move_history_wizard.py
│   └── expiration_report_wizard.py
├── report/
│   ├── bon_transfert_report.xml
│   ├── bon_entree_report.xml
│   ├── bon_sortie_report.xml
│   ├── lot_list_report.xml
│   ├── expiration_alert_report.xml
│   └── stock_history_report.xml
└── static/
    └── description/
        └── icon.png
```

### B. Fonctionnalites detaillees

#### 1. Menu Principal MAGIMED Interne
```
MAGIMED Interne
├── Tableau de Bord
│   ├── Alertes Expiration (widget)
│   ├── Mouvements du jour (widget)
│   └── Cautions a recuperer (widget)
├── Operations Stock
│   ├── Transferts Internes (raccourci + amelioration)
│   ├── Bons d'Entree (Production/Autres)
│   └── Bons de Sortie (Consommation/Rebuts)
├── Tracabilite
│   ├── Gestion des Lots
│   ├── Alertes Expiration
│   └── Historique Mouvements
└── Cautions
    └── Factures avec Caution
```

#### 2. Gestion des Lots et Numeros de Serie

**2.1 Extension du Produit (product.template)**
```python
# Nouveaux champs
- tracking = Selection [('none', 'lot', 'serial')]  # Standard Odoo
- use_expiration_date = Boolean                      # Standard Odoo
- expiration_alert_days = Integer (defaut: 30)       # Alerte X jours avant
- auto_lot_on_receipt = Boolean                      # Generation auto lot reception
- lot_prefix = Char                                  # Prefixe lot (ex: PROD-)
```

**2.2 Extension du Lot (stock.production.lot)**
```python
# Champs supplementaires
- alert_date = Date (compute: expiration_date - alert_days)
- is_expired = Boolean (compute)
- days_to_expiration = Integer (compute)
- total_qty = Float (compute: somme des quants)
- location_ids = Many2many (compute: emplacements contenant ce lot)
```

**2.3 Saisie Simplifiee du Lot**
- Wizard de creation rapide lors de la reception
- Generation automatique du numero de lot (sequence)
- Saisie de la date d'expiration obligatoire si configuree
- Calcul automatique de la date d'alerte

#### 3. Types d'Operations de Stock

**3.1 Bon d'Entree (Stock Entry)**
```
Sequence: BE/YYYY/XXXXX
Type: Entree Stock
Emplacement source: Fournisseurs/Production
Emplacement destination: Stock
Cas d'usage:
- Entree production (Produits finis)
- Entree manuelle (hors achats)
- Regularisation positive
```

**3.2 Bon de Sortie (Stock Exit)**
```
Sequence: BS/YYYY/XXXXX
Type: Sortie Stock
Emplacement source: Stock
Emplacement destination: Consommation/Rebut
Cas d'usage:
- Consommation matieres premieres
- Mise au rebut
- Regularisation negative
```

**3.3 Bon de Transfert (Ameliore)**
```
Sequence: BT/YYYY/XXXXX
Type: Transfert Interne
Informations supplementaires:
- Entrepot Source + Emplacement
- Entrepot Destination + Emplacement
- Numero de Lot (si applicable)
- Date d'expiration du lot
- Quantite transferee
```

#### 4. Rapport Bon de Transfert Ameliore

**Contenu du rapport:**
```
┌─────────────────────────────────────────────────────────────┐
│                    BON DE TRANSFERT                         │
│                    N°: BT/2026/00001                        │
├─────────────────────────────────────────────────────────────┤
│ Date: 25/01/2026          │ Responsable: [Utilisateur]      │
├─────────────────────────────────────────────────────────────┤
│ ENTREPOT SOURCE           │ ENTREPOT DESTINATION            │
│ Depot Central             │ Depot Conditionnement           │
│ Emplacement: WH/Stock     │ Emplacement: COND/Stock         │
├─────────────────────────────────────────────────────────────┤
│ PRODUITS TRANSFERES                                         │
├──────┬────────────────┬─────┬────────────┬─────────────────┤
│ Ref  │ Designation    │ Qte │ N° Lot     │ Date Expiration │
├──────┼────────────────┼─────┼────────────┼─────────────────┤
│ P001 │ Film PE 500m   │ 100 │ LOT-2026-01│ 31/12/2027      │
│ P002 │ Carton 40x30   │ 200 │ -          │ -               │
└──────┴────────────────┴─────┴────────────┴─────────────────┘
```

#### 5. Alertes d'Expiration

**5.1 Vue Liste Alertes**
- Liste des lots avec expiration proche (< X jours)
- Filtres: Par produit, categorie, entrepot, emplacement
- Tri par urgence (jours restants)
- Couleurs: Rouge (< 7j), Orange (< 30j), Jaune (< 60j)

**5.2 Rapport Alertes Expiration**
```
┌─────────────────────────────────────────────────────────────┐
│            ALERTE EXPIRATION - 25/01/2026                   │
├──────┬────────────┬────────────┬──────────┬────────────────┤
│ Lot  │ Produit    │ Expiration │ Jours    │ Quantite/Empl. │
├──────┼────────────┼────────────┼──────────┼────────────────┤
│ L001 │ Gants M    │ 01/02/2026 │ 7 [!]    │ 500 @ WH/Stock │
│ L002 │ Masques    │ 15/02/2026 │ 21 [!]   │ 1000 @ WH/Stock│
└──────┴────────────┴────────────┴──────────┴────────────────┘
```

**5.3 Notification Automatique**
- Email quotidien aux responsables
- Alerte dans le tableau de bord
- Activite planifiee pour suivi

#### 6. Historique des Mouvements

**6.1 Filtres Disponibles**
- Par produit (many2many)
- Par lot (many2many)
- Par categorie produit
- Par date (de - a)
- Par entrepot (many2many)
- Par emplacement (many2many, filtre dynamique selon entrepots)
- Par type d'operation (Entree/Sortie/Transfert/Livraison/Reception)

**6.2 Champs Affiches**
- Date mouvement
- Reference operation
- Type operation
- Produit
- Numero de lot
- Date expiration lot
- Quantite
- Emplacement source
- Emplacement destination
- Utilisateur responsable

**6.3 Export et Impression**
- Export Excel
- Impression PDF avec filtres appliques

#### 7. Gestion des Cautions (Factures)

**7.1 Extension Facture Client (account.move)**
```python
# Nouveaux champs
- has_caution = Boolean ("Cette facture a une caution")
- caution_duration_months = Integer (defaut: 24)
- caution_refund_date = Date (compute: date_facture + duration)
- caution_alert_days = Integer (defaut: 30)
- caution_alert_date = Date (compute: refund_date - alert_days)
- caution_status = Selection [('pending', 'alert', 'due', 'refunded')]
```

**7.2 Vue Factures avec Caution**
- Liste filtree des factures avec caution
- Colonnes: N° Facture, Client, Date, Montant, Date Remboursement, Statut
- Filtres: Statut caution, Client, Date echeance

**7.3 Alertes Caution**
- Notification X jours avant echeance
- Vue kanban par statut
- Rapport des cautions a rembourser

---

## IV. PLAN DE MIGRATION

### Phase 1: Preparation (Jour 1-2)

#### 1.1 Sauvegarde
```bash
# Backup complet de la base actuelle
pg_dump o15_magimed > o15_magimed_backup_$(date +%Y%m%d).sql

# Creation de la nouvelle base
createdb o15_magimed_iso
pg_restore -d o15_magimed_iso o15_magimed_backup.sql
```

#### 1.2 Analyse des pickings en cours
```sql
-- Lister les pickings a traiter
SELECT
    sp.name, sp.state, sp.scheduled_date,
    spt.name as type_operation,
    COUNT(sm.id) as nb_lignes
FROM stock_picking sp
JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
LEFT JOIN stock_move sm ON sm.picking_id = sp.id
WHERE sp.state NOT IN ('done', 'cancel')
GROUP BY sp.id, spt.name
ORDER BY sp.scheduled_date;
```

### Phase 2: Nettoyage des operations (Jour 3-4)

#### 2.1 Traitement des pickings en cours
```sql
-- Option 1: Annuler les brouillons
UPDATE stock_picking SET state = 'cancel'
WHERE state = 'draft';

-- Option 2: Pour les pickings assigned/confirmed
-- Creer un script Python pour valider avec ajustement d'inventaire
```

#### 2.2 Script de validation forcee
```python
# Script a executer dans Odoo shell
pickings = env['stock.picking'].search([
    ('state', 'in', ['assigned', 'confirmed'])
])
for picking in pickings:
    for move in picking.move_ids:
        # Forcer la quantite faite = quantite demandee
        for move_line in move.move_line_ids:
            move_line.qty_done = move_line.product_uom_qty
    try:
        picking.button_validate()
    except Exception as e:
        print(f"Erreur picking {picking.name}: {e}")
```

### Phase 3: Activation gestion des lots (Jour 5)

#### 3.1 Activation dans les parametres
```sql
-- Verifier le parametre systeme
UPDATE ir_config_parameter
SET value = 'True'
WHERE key = 'stock.group_stock_production_lot';

-- Activer le groupe pour les utilisateurs concernes
INSERT INTO res_groups_users_rel (gid, uid)
SELECT g.id, u.id
FROM res_groups g, res_users u
WHERE g.name = 'Manage Lots / Serial Numbers'
AND u.active = True
AND NOT EXISTS (
    SELECT 1 FROM res_groups_users_rel r
    WHERE r.gid = g.id AND r.uid = u.id
);
```

#### 3.2 Forcer le tracking sur les produits
```sql
-- Activer le tracking par lot pour tous les produits stockables
UPDATE product_template
SET tracking = 'lot',
    use_expiration_date = True
WHERE type = 'product';

-- Pour les produits necessitant numero de serie
-- (a identifier avec le client)
UPDATE product_template
SET tracking = 'serial'
WHERE id IN (/* liste des IDs produits */);

-- Produits sans tracking (consommables)
UPDATE product_template
SET tracking = 'none'
WHERE type = 'consu';
```

### Phase 4: Creation des entrepots (Jour 6)

#### 4.1 Nouveaux entrepots
```sql
-- Depot Conditionnement
INSERT INTO stock_warehouse (name, code, company_id, partner_id)
VALUES ('Depot Conditionnement', 'COND', 1, 1);

-- Depot Production (si necessaire)
INSERT INTO stock_warehouse (name, code, company_id, partner_id)
VALUES ('Depot Production', 'PROD', 1, 1);
```

#### 4.2 Configuration des emplacements
- Creer les emplacements internes pour chaque entrepot
- Configurer les routes de transfert

### Phase 5: Installation du module (Jour 7)

#### 5.1 Installation
```bash
# Copier le module
cp -r adi_magimed /path/to/addons/

# Mettre a jour la liste des modules
./odoo-bin -c odoo.conf -d o15_magimed_iso -u base --stop-after-init

# Installer le module
./odoo-bin -c odoo.conf -d o15_magimed_iso -i adi_magimed --stop-after-init
```

### Phase 6: Configuration et tests (Jour 8-10)

#### 6.1 Configuration
- Parametrage des sequences
- Configuration des types d'operations
- Definition des alertes d'expiration
- Configuration des emails de notification

#### 6.2 Tests
- Test creation lot avec date expiration
- Test bon d'entree
- Test bon de sortie
- Test transfert avec lot
- Test alertes expiration
- Test cautions factures

### Phase 7: Formation et mise en production

#### 7.1 Formation utilisateurs
- Session 1: Gestion des lots et dates d'expiration
- Session 2: Bons d'entree et sortie
- Session 3: Transferts et tracabilite
- Session 4: Historique et rapports
- Session 5: Gestion des cautions

#### 7.2 Reinventaire
- Inventaire initial avec lots
- Saisie des dates d'expiration existantes

---

## V. FONCTIONNALITES SUPPLEMENTAIRES PROPOSEES

### A. Suggestions d'ameliorations

#### 1. Tableau de Bord MAGIMED
- Widget alertes expiration (produits < 30 jours)
- Widget cautions a echeance
- Widget mouvements du jour
- Graphique stock par categorie

#### 2. Gestion des Certificats Qualite
```python
# Nouveau modele: magimed.quality.certificate
- name = Char
- lot_id = Many2one('stock.production.lot')
- certificate_type = Selection [('conformity', 'analysis', 'origin')]
- issue_date = Date
- expiry_date = Date
- document = Binary
- is_valid = Boolean (compute)
```

#### 3. Controle Qualite Reception
- Statut qualite sur reception (En attente, Conforme, Non conforme)
- Blocage des lots non conformes
- Workflow de validation qualite

#### 4. Etiquetage des Lots
- Generation d'etiquettes avec QR Code
- Contenu: Reference, Lot, Expiration, Emplacement
- Impression par lot ou par produit

#### 5. Statistiques et KPIs
- Taux de peremption
- Rotation des stocks par lot
- Delai moyen de consommation
- Valeur des stocks par date d'expiration

#### 6. Integration Scanner Code-Barres
- Scan rapide pour creation de lot
- Scan pour transfert
- Scan pour inventaire

#### 7. Alertes Avancees
- Notification push mobile (si app mobile)
- Escalade des alertes non traitees
- Tableau de bord alertes avec priorites

---

## VI. OFFRE COMMERCIALE

### A. Resume du Projet

| Element | Description |
|---------|-------------|
| **Client** | MAGIMED |
| **Projet** | Mise en conformite ISO - Tracabilite complete |
| **Solution** | Module Odoo 15 personnalise (adi_magimed) |

### B. Livrables

#### Phase 1: Migration et Preparation
| # | Livrable | Description |
|---|----------|-------------|
| 1.1 | Migration base | Duplication o15_magimed vers o15_magimed_iso |
| 1.2 | Nettoyage donnees | Validation/annulation des operations en cours |
| 1.3 | Activation lots | Configuration systeme pour gestion lots |
| 1.4 | Configuration produits | Mise a jour tracking sur produits |
| 1.5 | Creation entrepots | Depot Conditionnement + Depot Production |

#### Phase 2: Developpement Module adi_magimed
| # | Livrable | Description |
|---|----------|-------------|
| 2.1 | Menu MAGIMED Interne | Application principale avec navigation |
| 2.2 | Gestion Lots amelioree | Champs supplementaires, saisie simplifiee |
| 2.3 | Bon d'Entree Stock | Type operation + rapport |
| 2.4 | Bon de Sortie Stock | Type operation + rapport |
| 2.5 | Bon de Transfert | Rapport ameliore avec lots |
| 2.6 | Alertes Expiration | Vue + Rapport + Notifications |
| 2.7 | Historique Mouvements | Vue filtrable + Rapport |
| 2.8 | Gestion Cautions | Champs facture + Vue + Alertes |

#### Phase 3: Formation et Accompagnement
| # | Livrable | Description |
|---|----------|-------------|
| 3.1 | Formation Lots/Series | 2h - Utilisateurs cles |
| 3.2 | Formation Operations | 2h - Equipe stock |
| 3.3 | Formation Tracabilite | 1h - Responsables qualite |
| 3.4 | Formation Cautions | 1h - Equipe comptable |
| 3.5 | Documentation | Guide utilisateur complet |
| 3.6 | Accompagnement | Support post-mise en production (1 semaine) |

### C. Valeur Ajoutee

#### Pour la Conformite ISO
| Benefice | Impact |
|----------|--------|
| **Tracabilite complete** | Suivi de chaque lot de la reception a la livraison |
| **Documentation** | Rapports imprimes pour audits |
| **Historique** | Conservation des mouvements avec horodatage |
| **Alertes proactives** | Prevention des perempties et non-conformites |

#### Pour l'Efficacite Operationnelle
| Benefice | Impact |
|----------|--------|
| **Saisie simplifiee** | Reduction du temps de saisie lots |
| **Vision claire** | Menu dedie sans complexite production |
| **Alertes automatiques** | Plus d'oublis sur expirations et cautions |
| **Rapports personnalises** | Documents adaptes aux besoins MAGIMED |

#### Pour la Direction
| Benefice | Impact |
|----------|--------|
| **Reduction pertes** | Suivi des expirations = moins de rebuts |
| **Suivi cautions** | Recuperation systematique des cautions |
| **Decisions eclairees** | Historique detaille des mouvements |
| **Image professionnelle** | Documents aux normes pour clients |

### D. Planning Previsionnel

```
Semaine 1: Migration et Preparation
├── Jour 1-2: Sauvegarde et duplication base
├── Jour 3-4: Nettoyage operations en cours
└── Jour 5: Activation lots + Configuration

Semaine 2: Developpement (Partie 1)
├── Jour 1-2: Structure module + Menu
├── Jour 3-4: Gestion lots amelioree
└── Jour 5: Types operations (BE/BS)

Semaine 3: Developpement (Partie 2)
├── Jour 1-2: Rapports (BE/BS/BT)
├── Jour 3-4: Alertes expiration
└── Jour 5: Historique mouvements

Semaine 4: Finalisation et Formation
├── Jour 1-2: Gestion cautions
├── Jour 3: Tests complets
├── Jour 4: Formation utilisateurs
└── Jour 5: Mise en production

Semaine 5: Accompagnement
└── Support post-production
```

### E. Prerequis Client

1. **Disponibilite** des utilisateurs cles pour la formation
2. **Acces** a la base de production pour analyse
3. **Liste** des produits necessitant numero de serie (vs lot)
4. **Liste** des produits sans tracking
5. **Inventaire** physique prevu apres migration
6. **Validation** des maquettes de rapports

---

## VII. ANNEXES

### A. Maquettes des Rapports

[A definir avec le client - exemples fournis dans la section IV]

### B. Liste des Configurations

#### B.1 Types d'Operations
| Code | Nom | Source | Destination |
|------|-----|--------|-------------|
| BE | Bon d'Entree | Production/Virtual | Stock |
| BS | Bon de Sortie | Stock | Consommation/Virtual |
| BT | Bon de Transfert | Stock A | Stock B |

#### B.2 Sequences
| Code | Format | Exemple |
|------|--------|---------|
| BE | BE/%(year)s/%(seq)05d | BE/2026/00001 |
| BS | BS/%(year)s/%(seq)05d | BS/2026/00001 |
| BT | BT/%(year)s/%(seq)05d | BT/2026/00001 |
| LOT | %(prefix)s%(year)s%(month)s-%(seq)04d | PROD2601-0001 |

### C. Droits d'Acces

| Groupe | Operations | Alertes | Cautions | Config |
|--------|------------|---------|----------|--------|
| Utilisateur Stock | Lecture/Ecriture | Lecture | - | - |
| Responsable Stock | Complet | Lecture/Ecriture | - | Lecture |
| Comptable | Lecture | - | Lecture/Ecriture | - |
| Directeur | Complet | Complet | Complet | Complet |

---

**Document prepare le:** 25/01/2026
**Version:** 1.0
**Auteur:** Claude (Assistant IA)

---

*Ce document est un plan de travail et une offre commerciale. Les delais et fonctionnalites peuvent etre ajustes selon les besoins specifiques du client.*
