# TODO - Module adi_return_management

## Ameliorations a venir

### 1. ~~Prix de vente original~~ ✅ TERMINE (v15.0.2.1.0)
**Priorite:** ~~Haute~~ Terminé

~~Actuellement, le prix unitaire est recupere depuis `product.lst_price` (prix catalogue).~~

**Implementation realisee:**
Le prix de vente est maintenant recupere depuis la commande client d'origine.

**Champs ajoutes sur `return.order.line`:**
- `sale_line_id`: Lien vers la ligne de commande d'origine (pour tracer le prix)
- `origin_picking_id`: BL d'origine en mode souple
- `effective_picking_id`: Champ compute affichant le BL effectif (strict ou souple)

**Logique implementee:**

```
Mode STRICT:
  picking_line_id → picking_id → sale_id → sale.order.line → price_unit ✅

Mode SOUPLE:
  Recherche automatique dans les BL livres (order by date_done desc)
  → picking.sale_id → sale.order.line → price_unit ✅
  → Stockage du BL d'origine dans origin_picking_id

Mode LIBRE:
  Prix catalogue (lst_price) par defaut ✅
```

**Cas particuliers geres:**
- ✅ Produit vendu a plusieurs prix → prend le prix de la derniere vente
- ✅ Produit jamais vendu (mode libre) → prix catalogue par defaut
- ✅ Remises incluses dans le prix

---

### 2. ~~Amelioration des vues retour~~ ✅ TERMINE (v15.0.3.0.0)
**Priorite:** ~~Moyenne~~ Termine

**Ameliorations realisees:**

**Vue Kanban amelioree:**
- [x] Affichage du montant total en evidence
- [x] Badge avec nombre de produits
- [x] Badge raison de retour
- [x] Indicateurs visuels (picking/avoir cree)
- [x] Avatar utilisateur responsable
- [x] Widget activites

**Vue Tree amelioree:**
- [x] Colonne "Nb lignes" (nombre de produits)
- [x] Colonne "Jours" (anciennete)
- [x] Decoration rouge pour retours en retard
- [x] Widget activites
- [x] Sample data pour preview

**Vue Search amelioree (filtres):**
- [x] Filtres par periode: aujourd'hui, semaine, mois, mois dernier, trimestre, annee
- [x] Filtres par montant: petits (<10K), moyens (10K-50K), gros (>50K)
- [x] Filtres speciaux: en attente d'avoir, avec activites, activites en retard
- [x] Groupements: jour, semaine, mois, trimestre, annee, responsable

**Vue Formulaire amelioree:**
- [x] Nouvel onglet "Informations" avec statistiques
- [x] Affichage de l'anciennete et indicateur retard
- [x] Liens vers documents lies (picking, avoir)
- [x] Infos systeme (creation/modification) pour admins

**Champs ajoutes sur `return.order`:**
- `line_count`: Nombre de lignes (computed, stored)
- `days_since_creation`: Anciennete en jours (computed)
- `is_late`: Indicateur de retard (computed)

---

### 3. ~~Menu Analyse des retours~~ ✅ TERMINE (v15.0.2.2.0)
**Priorite:** ~~Moyenne~~ Termine

**Implementation realisee:**

**Vues creees dans `views/return_order_analysis_views.xml`:**
- [x] **Vue Pivot (TCD)** - Tableau croise dynamique
- [x] **Vue Graph ligne** - Evolution des retours dans le temps
- [x] **Vue Graph camembert** - Repartition par raison
- [x] **Vue Graph barres** - Top clients
- [x] **Vue Graph barres** - Retours par entrepot
- [x] **Vue Search** - Filtres par periode (mois, trimestre, annee)

**Menus ajoutes dans `views/return_menu.xml`:**
- [x] Tableau croise dynamique
- [x] Evolution des retours
- [x] Retours par raison
- [x] Retours par client
- [x] Retours par entrepot

**Filtres disponibles:**
- Ce mois / Mois dernier / Ce trimestre / Cette annee
- Par etat (brouillon, valide, avoir cree)
- Mes retours
- Groupement par client, raison, entrepot, etat, periode

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
│   ├── return_order_analysis_views.xml  # NEW - Vues Pivot/Graph
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

### v15.0.3.0.0 (actuelle)
- **Ameliorations des vues** ✅
  - Vue Kanban enrichie (montant, badges, indicateurs, avatar)
  - Vue Tree avec colonnes supplementaires (lignes, anciennete)
  - Decoration rouge pour retours en retard
  - Filtres par periode, montant, activites
  - Nouvel onglet "Informations" dans le formulaire
  - Champs `line_count`, `days_since_creation`, `is_late`

### v15.0.2.2.0
- **Menu Analyse des retours** ✅
  - Vue Pivot (tableau croise dynamique)
  - Vue Graph ligne (evolution dans le temps)
  - Vue Graph camembert (repartition par raison)
  - Vue Graph barres (top clients, par entrepot)
  - Filtres par periode (mois, trimestre, annee)

### v15.0.2.1.0
- **Prix de vente original depuis commande** ✅
  - Champ `sale_line_id` pour tracer la ligne de commande
  - Champ `origin_picking_id` pour le BL d'origine (mode souple)
  - Champ `effective_picking_id` (compute) pour le BL effectif
  - Recherche automatique du dernier prix de vente

### v15.0.2.0.0
- Module de base fonctionnel
- 3 modes d'origine (libre, souple, strict)
- Creation automatique picking + avoir
- Rapport bon de retour (non valorise)
- Filtrage entrepot par equipe commerciale
- Filtrage emplacement par entrepot

### v15.0.4.0.0 (future)
- Retours fournisseurs (a confirmer)
