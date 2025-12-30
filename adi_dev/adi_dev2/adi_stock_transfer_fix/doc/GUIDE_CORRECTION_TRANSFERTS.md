# Guide de Correction des Transferts Bloqués

## Table des Matières

1. [Comprendre le Problème](#1-comprendre-le-problème)
2. [Ordre d'Installation Recommandé](#2-ordre-dinstallation-recommandé)
3. [Flux Normal d'un Transfert](#3-flux-normal-dun-transfert)
4. [Types de Blocages](#4-types-de-blocages)
5. [Démarche de Correction](#5-démarche-de-correction)
6. [Utilisation du Module](#6-utilisation-du-module)
7. [Requêtes SQL de Diagnostic](#7-requêtes-sql-de-diagnostic)
8. [Prévention Future](#8-prévention-future)

---

## 1. Comprendre le Problème

### Symptôme Principal
```
"Transfert impossible! Le produit [XXX] n'a pas assez de stock
dans l'emplacement source 'Virtual Locations/Inter-company transit'"
```

### Cause Racine
Le module `adi_stock_transfer` original ne gère pas correctement les cas où :
- Le wizard de backorder apparaît (quantités partielles)
- Le picking source n'est pas validé mais le transfert passe en état "in_transit"
- Le stock n'est jamais transféré vers l'emplacement de transit

### Conséquence
- Transfert bloqué en état "in_transit"
- Picking source en état "assigned" (non validé)
- Stock = 0 dans le transit
- Impossible de terminer le transfert

---

## 2. Ordre d'Installation Recommandé

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORDRE D'INSTALLATION CRITIQUE                            │
└─────────────────────────────────────────────────────────────────────────────┘

  ╔═══════════════════════════════════════════════════════════════════════╗
  ║  ÉTAPE 1: CORRIGER D'ABORD LES TRANSFERTS EXISTANTS                   ║
  ║  ────────────────────────────────────────────────────────────────────  ║
  ║                                                                        ║
  ║  POURQUOI ?                                                            ║
  ║  • Le module enhanced modifie le comportement des transferts          ║
  ║  • Les anciens transferts bloqués ont été créés avec l'ancien code   ║
  ║  • Il faut les corriger avec la même logique qui les a créés         ║
  ║                                                                        ║
  ║  COMMENT ?                                                             ║
  ║  1. Installer adi_stock_transfer_fix                                  ║
  ║  2. Utiliser les outils de diagnostic et correction                   ║
  ║  3. Corriger TOUS les transferts bloqués                              ║
  ║  4. Vérifier qu'aucun transfert n'est en état incohérent             ║
  ╚═══════════════════════════════════════════════════════════════════════╝
                                    │
                                    ▼
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║  ÉTAPE 2: INSTALLER LE MODULE ENHANCED                                ║
  ║  ────────────────────────────────────────────────────────────────────  ║
  ║                                                                        ║
  ║  POURQUOI APRÈS ?                                                      ║
  ║  • Évite les conflits entre ancien et nouveau comportement            ║
  ║  • Base de données propre avant nouvelle logique                      ║
  ║  • Les nouveaux transferts bénéficieront de la correction             ║
  ║                                                                        ║
  ║  CE QUE FAIT LE MODULE ENHANCED :                                      ║
  ║  • Ajoute skip_backorder=True pour éviter le wizard                   ║
  ║  • Vérifie les stocks avant départ                                    ║
  ║  • Gère proprement les quantités partielles                           ║
  ║  • Crée des backorders au lieu de bloquer                             ║
  ╚═══════════════════════════════════════════════════════════════════════╝
                                    │
                                    ▼
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║  ÉTAPE 3: GARDER LE MODULE FIX INSTALLÉ                               ║
  ║  ────────────────────────────────────────────────────────────────────  ║
  ║                                                                        ║
  ║  POURQUOI ?                                                            ║
  ║  • Outil de surveillance continue                                     ║
  ║  • Détection des anomalies futures                                    ║
  ║  • Correction des pickings Odoo natifs bloqués                        ║
  ║  • Interface de diagnostic pratique                                   ║
  ╚═══════════════════════════════════════════════════════════════════════╝
```

### Résumé de l'Ordre

| Étape | Action | Module |
|-------|--------|--------|
| 1 | Installer | `adi_stock_transfer_fix` |
| 2 | Corriger | Tous les transferts bloqués |
| 3 | Vérifier | Aucun transfert incohérent |
| 4 | Installer | `adi_stock_transfer_enhanced` |
| 5 | Garder | Les deux modules actifs |

---

## 3. Flux Normal d'un Transfert

### Schéma du Flux Correct

```
  DÉPÔT SOURCE                    TRANSIT                      DÉPÔT DESTINATION
  ┌──────────┐                  ┌──────────┐                    ┌──────────┐
  │  Stock   │                  │  Stock   │                    │  Stock   │
  │  100 pcs │                  │   0 pcs  │                    │   0 pcs  │
  └──────────┘                  └──────────┘                    └──────────┘
       │                              │                              │
       │  1. DÉPART TRANSIT           │                              │
       │  (Picking Source = done)     │                              │
       ▼                              ▼                              │
  ┌──────────┐                  ┌──────────┐                         │
  │  Stock   │  ──────────────► │  Stock   │                         │
  │  70 pcs  │   -30 pcs        │  30 pcs  │                         │
  └──────────┘                  └──────────┘                         │
       │                              │                              │
       │                              │  2. RÉCEPTION               │
       │                              │  (Picking Dest = done)       │
       │                              ▼                              ▼
       │                        ┌──────────┐                  ┌──────────┐
       │                        │  Stock   │  ──────────────► │  Stock   │
       │                        │   0 pcs  │   -30 pcs        │  30 pcs  │
       │                        └──────────┘                  └──────────┘
```

### États Attendus

| Phase | Transfert | Picking Source | Picking Dest | Stock Transit |
|-------|-----------|----------------|--------------|---------------|
| Création | draft | - | - | 0 |
| Confirmation | confirmed | assigned | - | 0 |
| Départ | in_transit | **done** | assigned | **> 0** |
| Arrivée | done | done | **done** | 0 |

---

## 4. Types de Blocages

### Type A : Picking Source Non Validé

```
  PROBLÈME:
  ┌─────────────────────────────────────────┐
  │  Transfert.state = 'in_transit'         │
  │  Picking Source.state = 'assigned' ❌   │
  │  Stock Transit = 0 ❌                   │
  └─────────────────────────────────────────┘

  CAUSE: Le wizard backorder a bloqué la validation

  SOLUTION: Valider le picking source avec skip_backorder=True
```

### Type B : Stock Négatif dans le Transit

```
  PROBLÈME:
  ┌─────────────────────────────────────────┐
  │  Stock Transit < 0 (négatif) ❌         │
  │  Généralement dû à des corrections      │
  │  manuelles incorrectes                  │
  └─────────────────────────────────────────┘

  CAUSE: Corrections SQL partielles ou erreurs de manipulation

  SOLUTION: Corriger les quants dans le transit
```

### Type C : Stock Source Insuffisant

```
  PROBLÈME:
  ┌─────────────────────────────────────────┐
  │  Stock Source < Quantité Demandée ❌    │
  │  Le picking ne peut pas être validé     │
  └─────────────────────────────────────────┘

  CAUSE: Stock consommé par d'autres opérations

  SOLUTIONS:
  1. Ajuster les quantités du picking
  2. Réapprovisionner le stock source
  3. Forcer la validation (créera du stock négatif)
```

---

## 5. Démarche de Correction

### Étape 1 : Diagnostic Global

```
┌─────────────────────────────────────────────────────────────────┐
│  MENU: Transferts > Configuration > Détecter Transferts Bloqués │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Le système détecte automatiquement:                            │
│  • Transferts "in_transit" avec picking source non validé       │
│  • Transferts "done" avec picking source non validé             │
│  • Transferts "done" avec picking destination non validé        │
└─────────────────────────────────────────────────────────────────┘
```

### Étape 2 : Analyse Individuelle

```
Pour chaque transfert bloqué détecté:

1. Ouvrir le formulaire de diagnostic
2. Cliquer sur "Analyser"
3. Le système affiche:
   • Type de problème
   • Produits concernés
   • Stock disponible vs demandé
   • Actions de correction possibles
```

### Étape 3 : Correction

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARBRE DE DÉCISION                            │
└─────────────────────────────────────────────────────────────────┘

                    Le picking source
                    est-il validé ?
                          │
              ┌───────────┴───────────┐
              │                       │
             NON                     OUI
              │                       │
              ▼                       ▼
     Stock source              Le stock est-il
     suffisant ?               dans le transit ?
          │                         │
    ┌─────┴─────┐             ┌─────┴─────┐
    │           │             │           │
   OUI         NON           OUI         NON
    │           │             │           │
    ▼           ▼             ▼           ▼
 Valider    Choisir:       Valider    Corriger
 picking    • Ajuster      picking    les quants
 source       quantités    dest       du transit
            • Forcer
            • Attendre
```

### Étape 4 : Vérification

```
Après chaque correction:

1. Vérifier l'état du transfert
2. Vérifier les stocks dans chaque emplacement
3. S'assurer que les pickings sont cohérents
4. Relancer la détection pour confirmer
```

---

## 6. Utilisation du Module

### Menu Principal

```
Transferts
└── Configuration
    ├── Détecter les Transferts Bloqués    ← Lance la détection
    ├── Transferts Bloqués                  ← Liste des diagnostics
    ├── Détecter les Pickings Bloqués      ← Pickings Odoo natifs
    └── Pickings Bloqués                    ← Liste des pickings
```

### Boutons d'Action (Transferts)

| Bouton | Action | Quand l'utiliser |
|--------|--------|------------------|
| Analyser | Détaille le problème | Toujours en premier |
| Corriger | Ouvre le wizard de correction | Après analyse |
| Voir Transfert | Ouvre le transfert original | Pour vérification |

### Boutons d'Action (Pickings)

| Bouton | Action | Risque |
|--------|--------|--------|
| Ajuster Quantités | Réduit aux disponibilités | Faible |
| Corriger Stocks Négatifs | Corrige les quants | Moyen |
| Forcer Validation | Valide malgré le stock | **Élevé** |

---

## 7. Requêtes SQL de Diagnostic

### 7.1 Identifier les Transferts Bloqués

```sql
-- Transferts en transit avec picking source non validé
SELECT
    t.name AS transfert,
    t.state AS etat_transfert,
    sp.name AS picking_source,
    sp.state AS etat_picking,
    dp.name AS picking_dest,
    dp.state AS etat_dest
FROM adi_stock_transfer t
LEFT JOIN stock_picking sp ON t.source_picking_id = sp.id
LEFT JOIN stock_picking dp ON t.dest_picking_id = dp.id
WHERE t.state = 'in_transit'
  AND sp.state != 'done';
```

### 7.2 Vérifier les Stocks dans le Transit

```sql
-- Tous les produits dans les emplacements de transit
SELECT
    pt.name AS produit,
    pp.default_code AS reference,
    sq.quantity AS quantite,
    sl.complete_name AS emplacement
FROM stock_quant sq
JOIN stock_location sl ON sq.location_id = sl.id
JOIN product_product pp ON sq.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE sl.usage = 'transit'
ORDER BY sq.quantity;
```

### 7.3 Identifier les Stocks Négatifs

```sql
-- Stocks négatifs (problématiques)
SELECT
    pt.name AS produit,
    sq.quantity AS quantite,
    sl.complete_name AS emplacement
FROM stock_quant sq
JOIN stock_location sl ON sq.location_id = sl.id
JOIN product_product pp ON sq.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE sq.quantity < 0
ORDER BY sq.quantity;
```

### 7.4 Analyser un Picking Spécifique

```sql
-- Détail des mouvements d'un picking
SELECT
    pt.name AS produit,
    sm.product_uom_qty AS qte_demandee,
    sm.quantity_done AS qte_faite,
    sm.state AS etat,
    sl_src.name AS source,
    sl_dst.name AS destination
FROM stock_move sm
JOIN stock_picking sp ON sm.picking_id = sp.id
JOIN product_product pp ON sm.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
JOIN stock_location sl_src ON sm.location_id = sl_src.id
JOIN stock_location sl_dst ON sm.location_dest_id = sl_dst.id
WHERE sp.name = 'D-BA/INT/00570'  -- Remplacer par le nom du picking
ORDER BY pt.name;
```

### 7.5 Corriger un Stock Négatif (avec prudence)

```sql
-- ATTENTION: À utiliser avec précaution
-- Exemple: Corriger le stock d'un produit dans le transit

-- 1. D'abord identifier le quant
SELECT id, product_id, location_id, quantity
FROM stock_quant
WHERE product_id = XXX AND location_id = YYY;

-- 2. Mettre à jour (si nécessaire)
UPDATE stock_quant
SET quantity = 30  -- Nouvelle quantité correcte
WHERE id = ZZZ;
```

---

## 8. Prévention Future

### Ce que fait le Module Enhanced

```
┌─────────────────────────────────────────────────────────────────┐
│              MODULE adi_stock_transfer_enhanced                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✓ skip_backorder=True                                         │
│    → Évite le blocage par le wizard de backorder               │
│    → Les quantités partielles créent un backorder automatique  │
│                                                                 │
│  ✓ Vérification des stocks avant départ                        │
│    → Avertissement si stock insuffisant                        │
│    → Option de forcer ou d'ajuster                             │
│                                                                 │
│  ✓ Gestion propre des quantités partielles                     │
│    → Backorder créé pour le reste                              │
│    → Pas de blocage du flux                                    │
│                                                                 │
│  ✓ Logging amélioré                                            │
│    → Traçabilité des opérations                                │
│    → Facilite le diagnostic                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Bonnes Pratiques

1. **Surveillance régulière**
   - Lancer la détection hebdomadairement
   - Traiter les blocages rapidement

2. **Formation utilisateurs**
   - Expliquer le flux de transfert
   - Ne pas annuler/modifier les pickings manuellement

3. **Sauvegardes**
   - Avant toute correction majeure
   - Dupliquer la base pour tester

4. **Documentation**
   - Noter les corrections effectuées
   - Identifier les patterns récurrents

---

## Annexe : Checklist de Correction

```
□ 1. Sauvegarder la base de données
□ 2. Lancer "Détecter les Transferts Bloqués"
□ 3. Pour chaque transfert bloqué:
    □ a. Ouvrir le diagnostic
    □ b. Cliquer sur "Analyser"
    □ c. Vérifier le stock source
    □ d. Choisir l'action appropriée
    □ e. Exécuter la correction
    □ f. Vérifier le résultat
□ 4. Relancer la détection (doit être vide)
□ 5. Installer adi_stock_transfer_enhanced
□ 6. Tester un nouveau transfert
□ 7. Vérifier le comportement avec quantités partielles
```

---

*Document créé le 30/12/2024 - Module adi_stock_transfer_fix v15.0.2.0.0*
