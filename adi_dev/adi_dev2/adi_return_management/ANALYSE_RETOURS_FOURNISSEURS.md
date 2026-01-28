# Analyse : Module Retours Fournisseurs

## 1. Resume executif

Ce document presente l'analyse complete pour l'implementation d'un systeme de gestion des **retours vers les fournisseurs** dans Odoo 15. Cette fonctionnalite permettra de gerer les produits defectueux, erreurs de livraison, et autres cas necessitant un retour au fournisseur.

---

## 2. Comparaison : Retours Clients vs Retours Fournisseurs

| Aspect | Retour Client (existant) | Retour Fournisseur (a creer) |
|--------|-------------------------|------------------------------|
| **Modele** | `return.order` | `supplier.return.order` |
| **Partenaire** | Client (`customer_rank > 0`) | Fournisseur (`supplier_rank > 0`) |
| **Document origine** | Commande vente (`sale.order`) | Commande achat (`purchase.order`) |
| **BL origine** | BL sortant (`outgoing`) | BL entrant (`incoming`) |
| **Avoir cree** | Avoir client (`out_refund`) | Avoir fournisseur (`in_refund`) |
| **Mouvement stock** | Client → Entrepot (ENTREE) | Entrepot → Fournisseur (SORTIE) |
| **Emplacement source** | `stock.stock_location_customers` | Emplacement interne (entrepot) |
| **Emplacement dest.** | Emplacement retour (interne) | `stock.stock_location_suppliers` |
| **Type picking** | Reception (`in_type_id`) | Expedition (`out_type_id`) |
| **Sequence** | `RET/2025/00001` | `RETF/2025/00001` |
| **Prix** | Prix vente original | Prix achat original |

---

## 3. Recommandation d'architecture

### Option retenue : Module SEPARE

**Nom du module :** `adi_supplier_return_management`

### Justification

| Critere | Module separe | Extension module existant |
|---------|--------------|--------------------------|
| **Clarte du code** | ✅ Code dedie, facile a maintenir | ❌ Code mixte, complexe |
| **Independence** | ✅ Peut etre installe seul | ❌ Depend du module client |
| **Droits d'acces** | ✅ Groupes dedies (acheteurs) | ❌ Melange avec vendeurs |
| **Evolution** | ✅ Evolutions independantes | ❌ Risque de regression |
| **Simplicite** | ✅ Logique metier claire | ❌ Conditions partout |

### Dependance

Le nouveau module `adi_supplier_return_management` sera **independant** du module `adi_return_management` existant. Il n'y aura pas de dependance entre les deux.

**Dependances requises :**
- `base`
- `purchase_stock` (commandes achat + stock)
- `account` (avoirs fournisseurs)
- `stock`

---

## 4. Specifications fonctionnelles

### 4.1 Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  BROUILLON  │────>│   VALIDE    │────>│ AVOIR CREE  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
   Saisie des        Picking sortie      Avoir fournisseur
   produits a        cree (expedition    cree (in_refund)
   retourner         vers fournisseur)
```

### 4.2 Cas d'utilisation

1. **Produit defectueux recu**
   - L'acheteur recoit un produit defectueux
   - Il cree un ordre de retour fournisseur
   - Il selectionne la commande achat / BL d'origine
   - Validation → creation du BL de sortie vers fournisseur
   - Creation de l'avoir fournisseur

2. **Erreur de livraison fournisseur**
   - Le fournisseur a livre le mauvais produit
   - Meme processus de retour

3. **Produit perrime recu**
   - Produit recu avec date de peremption depassee
   - Retour au fournisseur avec avoir

### 4.3 Modes d'origine (comme retours clients)

| Mode | Description |
|------|-------------|
| **Libre** | Choix libre des produits a retourner |
| **Souple** | Produits deja recus de ce fournisseur |
| **Strict** | Produits d'une commande achat / BL specifique |

---

## 5. Specifications techniques

### 5.1 Structure du module

```
adi_supplier_return_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── supplier_return_order.py      # Modele principal
│   ├── supplier_return_order_line.py # Lignes de retour
│   ├── supplier_return_reason.py     # Raisons de retour
│   ├── account_move.py               # Extension pour lien avoir
│   └── res_config_settings.py        # Parametres
├── views/
│   ├── supplier_return_order_views.xml
│   ├── supplier_return_reason_views.xml
│   ├── supplier_return_analysis_views.xml
│   ├── res_config_settings_views.xml
│   └── supplier_return_menu.xml
├── report/
│   ├── __init__.py
│   └── supplier_return_order_report.xml
├── security/
│   ├── supplier_return_security.xml
│   └── ir.model.access.csv
├── data/
│   └── supplier_return_data.xml
└── static/
    └── description/
        └── icon.png
```

### 5.2 Modele principal : `supplier.return.order`

```python
class SupplierReturnOrder(models.Model):
    _name = 'supplier.return.order'
    _description = 'Ordre de retour fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # === CHAMPS PRINCIPAUX ===
    name = fields.Char(string='Reference', required=True, readonly=True,
                       default=lambda self: _('Nouveau'))

    partner_id = fields.Many2one('res.partner', string='Fournisseur',
                                 required=True, tracking=True,
                                 domain="[('supplier_rank', '>', 0)]")

    date = fields.Date(string='Date du retour', required=True,
                       default=fields.Date.context_today)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Valide'),
        ('refund_created', 'Avoir cree'),
    ], string='Etat', default='draft', tracking=True)

    # === ORIGINE ===
    origin_mode = fields.Selection([
        ('none', 'Libre'),
        ('flexible', 'Souple'),
        ('strict', 'Strict'),
    ], string='Mode origine', compute='_compute_origin_mode')

    purchase_order_ids = fields.Many2many('purchase.order',
        string='Commandes achat',
        domain="[('partner_id', '=', partner_id), ('state', 'in', ['purchase', 'done'])]")

    picking_ids = fields.Many2many('stock.picking',
        string='Bons de reception',
        domain="[('purchase_id', 'in', purchase_order_ids), ('state', '=', 'done'), ('picking_type_code', '=', 'incoming')]")

    # === RAISON ===
    reason_id = fields.Many2one('supplier.return.reason',
                                string='Raison du retour', required=True)

    # === ENTREPOT / EMPLACEMENT ===
    warehouse_id = fields.Many2one('stock.warehouse', string='Entrepot',
                                   required=True)
    source_location_id = fields.Many2one('stock.location',
        string='Emplacement source',
        domain="[('usage', '=', 'internal')]",
        help="Emplacement d'ou partent les produits")

    # === LIGNES ===
    line_ids = fields.One2many('supplier.return.order.line',
                               'return_order_id', string='Lignes')

    # === DOCUMENTS LIES ===
    refund_id = fields.Many2one('account.move', string='Avoir fournisseur',
                                readonly=True)
    return_picking_id = fields.Many2one('stock.picking',
                                        string='Expedition retour', readonly=True)

    # === MONTANTS ===
    amount_total = fields.Monetary(string='Montant total',
                                   compute='_compute_amount_total', store=True)
    currency_id = fields.Many2one('res.currency', string='Devise')
```

### 5.3 Modele lignes : `supplier.return.order.line`

```python
class SupplierReturnOrderLine(models.Model):
    _name = 'supplier.return.order.line'
    _description = 'Ligne ordre de retour fournisseur'

    return_order_id = fields.Many2one('supplier.return.order',
                                      string='Ordre de retour', required=True)
    product_id = fields.Many2one('product.product', string='Produit',
                                 required=True)
    qty_returned = fields.Float(string='Quantite retournee', default=1.0)

    # Prix d'achat original
    price_unit = fields.Float(string='Prix unitaire',
                              compute='_compute_price_unit', store=True)
    purchase_line_id = fields.Many2one('purchase.order.line',
                                       string='Ligne commande origine')

    subtotal = fields.Monetary(string='Sous-total',
                               compute='_compute_subtotal', store=True)

    # Lien vers BL d'origine
    picking_line_id = fields.Many2one('stock.move.line',
                                      string='Ligne BL origine')
    origin_picking_id = fields.Many2one('stock.picking',
                                        string='BL origine (souple)')
```

### 5.4 Creation du picking de sortie

```python
def _create_return_picking(self):
    """Cree le picking de retour (sortie vers fournisseur)"""
    self.ensure_one()

    # Type d'operation: SORTIE (expedition)
    picking_type = self.warehouse_id.out_type_id

    # Emplacement destination: fournisseurs
    supplier_location = self.env.ref('stock.stock_location_suppliers')

    move_vals = []
    for line in self.line_ids:
        move_vals.append((0, 0, {
            'name': line.product_id.display_name,
            'product_id': line.product_id.id,
            'product_uom_qty': line.qty_returned,
            'product_uom': line.product_id.uom_id.id,
            'location_id': self.source_location_id.id,  # Emplacement interne
            'location_dest_id': supplier_location.id,    # Vers fournisseur
        }))

    picking = self.env['stock.picking'].create({
        'picking_type_id': picking_type.id,
        'partner_id': self.partner_id.id,
        'origin': self.name,
        'location_id': self.source_location_id.id,
        'location_dest_id': supplier_location.id,
        'move_ids_without_package': move_vals,
    })

    picking.action_confirm()
    picking.action_assign()

    return picking
```

### 5.5 Creation de l'avoir fournisseur

```python
def action_create_refund(self):
    """Cree l'avoir fournisseur (in_refund)"""
    self.ensure_one()

    invoice_lines = []
    for line in self.line_ids:
        # Taxes d'achat du produit
        taxes = line.product_id.supplier_taxes_id.filtered(
            lambda t: t.company_id == self.company_id
        )
        invoice_lines.append((0, 0, {
            'product_id': line.product_id.id,
            'quantity': line.qty_returned,
            'price_unit': line.price_unit,
            'name': line.product_id.display_name,
            'tax_ids': [(6, 0, taxes.ids)],
        }))

    # Type: avoir fournisseur (in_refund)
    refund = self.env['account.move'].create({
        'move_type': 'in_refund',  # <-- Difference cle
        'partner_id': self.partner_id.id,
        'invoice_date': self.date,
        'invoice_origin': self.name,
        'ref': _("Retour fournisseur %s - %s") % (self.name, self.reason_id.name),
        'supplier_return_order_id': self.id,
        'invoice_line_ids': invoice_lines,
    })

    self.write({
        'refund_id': refund.id,
        'state': 'refund_created',
    })

    return refund
```

---

## 6. Raisons de retour fournisseur

| Code | Raison | Description |
|------|--------|-------------|
| `DEFECT` | Produit defectueux | Defaut de fabrication |
| `WRONG` | Mauvais produit | Produit ne correspondant pas a la commande |
| `DAMAGED` | Produit endommage | Endommage pendant transport |
| `EXPIRED` | Produit perrime | Date de peremption depassee |
| `QUALITY` | Non-conformite qualite | Ne respecte pas les standards |
| `EXCESS` | Surplus de livraison | Quantite livree superieure a commandee |
| `OTHER` | Autre | Autre raison |

---

## 7. Securite et droits d'acces

### 7.1 Groupes

| Groupe | Description | Droits |
|--------|-------------|--------|
| `group_supplier_return_user` | Utilisateur retours fournisseurs | Lecture, creation, modification |
| `group_supplier_return_manager` | Responsable retours fournisseurs | Tous les droits + suppression |

### 7.2 Matrice des droits

| Modele | User | Manager |
|--------|------|---------|
| `supplier.return.order` | CRUD- | CRUD+ |
| `supplier.return.order.line` | CRUD+ | CRUD+ |
| `supplier.return.reason` | R--- | CRUD+ |

---

## 8. Menu et navigation

```
Achats (menu existant)
└── Retours fournisseurs (nouveau)
    ├── Operations
    │   └── Ordres de retour
    ├── Analyse
    │   ├── Tableau croise dynamique
    │   ├── Evolution des retours
    │   ├── Retours par raison
    │   └── Retours par fournisseur
    └── Configuration
        ├── Raisons de retour
        └── Parametres
```

**Alternative :** Creer un menu racine separe "Retours Fournisseurs" comme pour les retours clients.

---

## 9. Points d'attention

### 9.1 Gestion des garanties

**Question :** Faut-il gerer les garanties fournisseur ?

**Options :**
1. **Non** (v1) - Retour simple sans suivi garantie
2. **Oui** (v2) - Ajouter champs:
   - `warranty_claim` (boolean) - Retour sous garantie
   - `warranty_expiry_date` (date) - Date expiration garantie
   - `warranty_reference` (char) - Reference garantie

**Recommandation :** Commencer par v1, ajouter garanties en v2 si besoin.

### 9.2 Lien avec reclamations

**Question :** Faut-il lier aux reclamations fournisseur ?

Le module standard `purchase_complaint` n'existe pas dans Odoo.

**Options :**
1. **Non** (v1) - Module autonome
2. **Oui** (v2) - Creer un systeme de reclamations si besoin

**Recommandation :** Module autonome pour v1.

### 9.3 Filtrage par equipe d'achat

Comme pour les retours clients avec les equipes commerciales, on pourrait filtrer les entrepots par equipe d'achat. Cependant, les equipes d'achat sont moins courantes.

**Recommandation :** Pas de filtrage par equipe en v1. Tous les entrepots accessibles.

---

## 10. Estimation de l'effort

| Composant | Complexite | Estimation |
|-----------|------------|------------|
| Modeles (`supplier.return.order`, `supplier.return.order.line`) | Moyenne | Base du module client |
| Modele raisons | Faible | Copie simple |
| Vues (form, tree, kanban, search) | Moyenne | Adaptation du module client |
| Vues analyse (pivot, graph) | Faible | Copie + adaptation |
| Securite | Faible | Standard |
| Rapport PDF | Moyenne | Nouveau rapport |
| Tests | Moyenne | A prevoir |

**Total :** Effort modere grace a la reutilisation de la structure du module client.

---

## 11. Plan d'implementation

### Phase 1 : Base (prioritaire)
1. Structure du module
2. Modeles principaux
3. Vues de base (form, tree, kanban)
4. Workflow (brouillon → valide → avoir)
5. Securite

### Phase 2 : Ameliorations
1. Vues analyse (pivot, graph)
2. Rapport PDF
3. Prix d'achat original

### Phase 3 : Options (si besoin)
1. Gestion des garanties
2. Lien avec reclamations
3. Filtrage par equipe d'achat

---

## 12. Decision requise

Avant de proceder a l'implementation, merci de confirmer :

1. **Architecture :** Module separe `adi_supplier_return_management` ? ✅/❌

2. **Menu :** Sous-menu de "Achats" ou menu racine separe ?
   - [ ] Sous-menu "Achats"
   - [ ] Menu racine separe

3. **Raisons :** Utiliser les memes raisons que retours clients ou raisons specifiques ?
   - [ ] Memes raisons (modele partage)
   - [ ] Raisons specifiques (modele separe)

4. **Garanties :** Inclure la gestion des garanties en v1 ?
   - [ ] Oui
   - [ ] Non (reporter a v2)

5. **Rapport PDF :** Necessaire en v1 ?
   - [ ] Oui
   - [ ] Non (reporter)

---

## 13. Conclusion

L'implementation d'un module de retours fournisseurs est **faisable et relativement rapide** grace a :
- La structure existante du module retours clients
- L'experience acquise sur le module client
- La similarite des workflows

Le module sera **independant** et pourra etre installe/desinstalle separement du module retours clients.

---

*Document genere le : 2026-01-27*
*Module source : adi_return_management v15.0.3.0.0*
