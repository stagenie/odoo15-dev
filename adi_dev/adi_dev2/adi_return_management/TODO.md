# TODO - Module adi_return_management

## Ameliorations a venir

### 1. Prix de vente original
**Priorite:** Haute

Actuellement, le prix unitaire est recupere depuis `product.lst_price` (prix catalogue).

**Amelioration souhaitee:**
Recuperer le **prix de vente original** depuis la commande client associee au BL.

**Important:** Cette amelioration concerne **TOUS les modes** (strict ET souple) car:
- En mode **strict**: l'utilisateur selectionne des BL specifiques → on connait directement les commandes
- En mode **souple**: les produits viennent de TOUS les BL du client → on peut quand meme retrouver la commande d'origine

**Logique a implementer:**

```
Mode STRICT:
  Ligne retour → picking_line_id → picking_id → sale_id → sale.order.line (meme produit) → price_unit

Mode SOUPLE:
  Ligne retour → product_id + partner_id
  → Rechercher stock.picking (partner_id, state=done, outgoing)
  → picking.sale_id → sale.order.line (meme produit)
  → Prendre le prix de la derniere vente (ou proposer choix si plusieurs prix)
```

**Cas particuliers a gerer:**
- Produit vendu a **plusieurs prix differents** au meme client → proposer le dernier prix ou laisser l'utilisateur choisir
- Produit **jamais vendu** (mode libre) → utiliser le prix catalogue par defaut
- **Remises** → le prix dans `sale.order.line.price_unit` inclut deja la remise

**Fichiers concernes:**
- `models/return_order_line.py` - Modifier `_compute_price_unit()`
- Ajouter un champ `sale_line_id` (optionnel) pour tracer la ligne de commande d'origine
- Eventuellement ajouter un champ `origin_picking_id` sur la ligne pour tracer le BL d'origine en mode souple

---

### 2. Amelioration des vues retour
**Priorite:** Moyenne

**Ameliorations prevues:**
- [ ] Ameliorer la vue Kanban avec plus d'informations
- [ ] Ajouter des filtres supplementaires (par periode, par montant, etc.)
- [ ] Ajouter des groupements supplementaires
- [ ] Ameliorer la vue formulaire (disposition, champs optionnels)
- [ ] Ajouter des indicateurs visuels (couleurs selon etat, anciennete, etc.)

---

### 3. Menu Analyse des retours
**Priorite:** Moyenne

**Fonctionnalites a ajouter:**
- [ ] **Vue Pivot (TCD)** pour analyser:
  - Retours par client
  - Retours par raison
  - Retours par produit
  - Retours par periode (mois/trimestre/annee)
  - Retours par entrepot
  - Montants totaux des retours

- [ ] **Vue Graphique** avec:
  - Evolution des retours dans le temps (ligne)
  - Repartition par raison (camembert)
  - Top clients avec le plus de retours (barres)
  - Top produits retournes (barres)

**Fichiers a creer:**
- `views/return_order_analysis_views.xml` - Vues pivot et graph
- Mettre a jour `views/return_menu.xml` - Ajouter menu Analyse

**Modele:**
```xml
<!-- Vue Pivot -->
<record id="view_return_order_pivot" model="ir.ui.view">
    <field name="name">return.order.pivot</field>
    <field name="model">return.order</field>
    <field name="arch" type="xml">
        <pivot string="Analyse des retours">
            <field name="date" type="row" interval="month"/>
            <field name="reason_id" type="col"/>
            <field name="amount_total" type="measure"/>
        </pivot>
    </field>
</record>

<!-- Vue Graph -->
<record id="view_return_order_graph" model="ir.ui.view">
    <field name="name">return.order.graph</field>
    <field name="model">return.order</field>
    <field name="arch" type="xml">
        <graph string="Analyse des retours">
            <field name="date" type="row" interval="month"/>
            <field name="amount_total" type="measure"/>
        </graph>
    </field>
</record>
```

---

### 4. Retours fournisseurs (a discuter)
**Priorite:** Basse (phase 2)

**Concept:**
Creer un module similaire pour gerer les **retours vers les fournisseurs** (produits defectueux, erreurs de livraison, etc.)

**Points a considerer:**

| Aspect | Retour Client | Retour Fournisseur |
|--------|---------------|-------------------|
| Modele | `return.order` | `supplier.return.order` |
| Partenaire | Client (`customer_rank > 0`) | Fournisseur (`supplier_rank > 0`) |
| Origine | Commande vente / BL sortant | Commande achat / BL entrant |
| Document cree | Avoir client (`out_refund`) | Avoir fournisseur (`in_refund`) |
| Mouvement stock | Client → Entrepot (entree) | Entrepot → Fournisseur (sortie) |
| Emplacement source | `stock_location_customers` | Emplacement interne |
| Emplacement dest. | Emplacement retour | `stock_location_suppliers` |

**Options d'implementation:**
1. **Module separe** (`adi_supplier_return_management`) - Plus propre, independant
2. **Extension du module actuel** - Ajouter un champ `return_type` (client/fournisseur)

**Questions a resoudre:**
- Faut-il un workflow similaire (brouillon → valide → avoir)?
- Comment gerer les garanties fournisseur?
- Faut-il lier aux reclamations fournisseur?

---

## Notes techniques

### Dependances actuelles
- `base`
- `sale_stock`
- `account`
- `stock`
- `sales_team`
- `warehouse_restrictions_app`
- `adi_stock_transfer_report`

### Structure du module
```
adi_return_management/
├── __init__.py
├── __manifest__.py
├── TODO.md                          # Ce fichier
├── models/
│   ├── __init__.py
│   ├── return_order.py
│   ├── return_order_line.py
│   ├── return_reason.py
│   ├── account_move.py
│   └── res_config_settings.py
├── views/
│   ├── return_order_views.xml
│   ├── return_reason_views.xml
│   ├── res_config_settings_views.xml
│   └── return_menu.xml
├── report/
│   ├── __init__.py
│   └── return_order_report.xml
├── security/
│   ├── return_security.xml
│   └── ir.model.access.csv
├── data/
│   └── return_data.xml
└── static/
    └── description/
        └── icon.png
```

---

## Historique des versions

### v15.0.2.0.0 (actuelle)
- Module de base fonctionnel
- 3 modes d'origine (libre, souple, strict)
- Creation automatique picking + avoir
- Rapport bon de retour (non valorise)
- Filtrage entrepot par equipe commerciale
- Filtrage emplacement par entrepot

### v15.0.3.0.0 (prevue)
- Prix de vente original depuis commande
- Menu Analyse (pivot + graph)
- Ameliorations vues

### v15.0.4.0.0 (future)
- Retours fournisseurs (a confirmer)
