# Guide de Transfert de Stock Inter-Depots

## Introduction

Ce document decrit le processus complet de transfert de stock entre deux entrepots (A vers B) avec tous les scenarios possibles.

Les modules concernes sont:
- **adi_stock_transfer**: Module de base (transfert complet)
- **adi_stock_transfer_backorder**: Module complementaire (reception partielle et reliquats)

---

## 1. Emplacements Impliques

```
+------------------+     +------------------+     +------------------+
|    SOURCE (A)    |     |     TRANSIT      |     | DESTINATION (B)  |
|  Stock/Entrepot  | --> |  Inter-Depots    | --> |  Stock/Entrepot  |
+------------------+     +------------------+     +------------------+
```

| Emplacement | Type | Description |
|-------------|------|-------------|
| Source (A) | `internal` | Entrepot d'origine des produits |
| Transit | `transit` | Emplacement intermediaire pour suivi |
| Destination (B) | `internal` | Entrepot de reception des produits |

---

## 2. Workflow Principal

```
BROUILLON --> DEMANDE --> APPROUVE --> EN TRANSIT --> TERMINE
    |            |           |             |             |
    |            |           |             |             |
Demandeur    Demandeur   Validateur    Expediteur   Destinataire
  cree        soumet      approuve      envoie        recoit
```

### Etats du Transfert

| Etat | Code | Description | Actions Disponibles |
|------|------|-------------|---------------------|
| Brouillon | `draft` | Transfert en cours de creation | Soumettre, Annuler |
| Demande | `requested` | En attente de validation | Approuver, Annuler |
| Approuve | `approved` | Valide, pret a etre envoye | Envoyer, Annuler |
| En Transit | `in_transit` | Produits en cours de transfert | Reception complete, Reception partielle |
| Reception Partielle | `partial` | Reception incomplete, reliquats a traiter | Traiter reliquats |
| Termine | `done` | Transfert complete | - |
| Annule | `cancelled` | Transfert annule | Remettre en brouillon |

---

## 3. Scenarios de Transfert

### Scenario 1: Transfert Complet (Module de base)

**Contexte**: Demande de 100 unites, tout est envoye et recu integralement.

```
Demande: 100 unites

ETAPE 1: BROUILLON
+-- Stock A: 100
+-- Transit: 0
+-- Stock B: 0

ETAPE 2: DEMANDE --> APPROUVE
+-- Stock A: 100 (reserve)
+-- Transit: 0
+-- Stock B: 0

ETAPE 3: ENVOYER (qty_sent = 100)
+-- Picking Sortie: A --> Transit [VALIDE]
+-- Stock A: 0
+-- Transit: 100
+-- Stock B: 0

ETAPE 4: TERMINER (Reception complete)
+-- Picking Entree: Transit --> B [VALIDE]
+-- Stock A: 0
+-- Transit: 0
+-- Stock B: 100 [OK]
```

**Resultat**: Transfert termine avec succes.

---

### Scenario 2: Reception Partielle avec Retour Expediteur

**Contexte**: 100 unites envoyees, seulement 70 recues. Les 30 restantes retournent a l'expediteur.

```
Demande: 100 | Envoye: 100 | Recu: 70 | Reliquat: 30

ETAPE 1-3: Identique au scenario 1
+-- Stock A: 0
+-- Transit: 100
+-- Stock B: 0

ETAPE 4: RECEPTION PARTIELLE (qty_received = 70)
+-- Etat: "Reception Partielle"
+-- Stock A: 0
+-- Transit: 30 (reliquat)
+-- Stock B: 70

ETAPE 5: TRAITER RELIQUATS - RETOUR EXPEDITEUR
+-- Mouvement: Transit --> A (30 unites)
+-- Stock A: 30 [Retour]
+-- Transit: 0
+-- Stock B: 70
```

**Resultat**: 70 unites a destination, 30 unites retournees a la source.

---

### Scenario 3: Reception Partielle avec Ajustement Inventaire

**Contexte**: 100 unites envoyees, 70 recues. Les 30 restantes sont perdues (casse, vol, etc.).

```
Demande: 100 | Envoye: 100 | Recu: 70 | Reliquat: 30

ETAPE 4: RECEPTION PARTIELLE (qty_received = 70)
+-- Etat: "Reception Partielle"
+-- Transit: 30 (reliquat)
+-- Stock B: 70

ETAPE 5: TRAITER RELIQUATS - AJUSTEMENT INVENTAIRE
+-- Mouvement: Transit --> Perte Inventaire (30 unites)
+-- Stock A: 0
+-- Transit: 0
+-- Stock B: 70
+-- Perte Inventaire: 30 [Enregistree]
```

**Resultat**: 70 unites a destination, 30 unites enregistrees comme perte.

---

### Scenario 4: Reception Partielle avec Report

**Contexte**: 100 unites envoyees, 70 recues. Les 30 restantes seront envoyees ulterieurement.

```
Demande: 100 | Envoye: 100 | Recu: 70 | Reliquat: 30

ETAPE 4: RECEPTION PARTIELLE (qty_received = 70)
+-- Etat: "Reception Partielle"
+-- Transit: 30 (reliquat)
+-- Stock B: 70

ETAPE 5: TRAITER RELIQUATS - REPORTER
+-- Nouveau transfert cree: TR/00XXX (30 unites)
+-- Transfert original: Termine
+-- Stock B: 70
+-- Transit: 30 (en attente du nouveau transfert)
```

**Resultat**: 70 unites a destination, nouveau transfert cree pour les 30 unites restantes.

---

### Scenario 5: Envoi Partiel par l'Expediteur

**Contexte**: Demande de 100 unites, mais l'expediteur n'a que 80 en stock.

```
Demande: 100 | Envoye: 80 | Stock disponible: 80

ETAPE 3: ENVOYER (qty_sent = 80)
+-- Stock A: 0 (avait 80 disponible)
+-- Transit: 80
+-- Stock B: 0

ETAPE 4: RECEPTION COMPLETE (80 unites)
+-- Stock A: 0
+-- Transit: 0
+-- Stock B: 80

Note: 20 unites jamais envoyees (ecart demande/envoi non gere)
```

**Resultat**: 80 unites transferees. L'ecart de 20 unites entre demande et envoi n'est pas automatiquement gere.

---

### Scenario 6: Annulation du Transfert

**Contexte**: Le transfert est annule avant l'envoi.

```
BROUILLON/DEMANDE/APPROUVE --> ANNULE

+-- Stock A: Inchange (ou libere si reserve)
+-- Transit: 0
+-- Stock B: Inchange
+-- Pickings: Annules si crees
```

**Resultat**: Aucun mouvement de stock effectue.

---

## 4. Schema des Mouvements de Stock

```
+-----------------------------------------------------------------------------+
|                        MOUVEMENTS DE STOCK                                   |
+-----------------------------------------------------------------------------+
|                                                                              |
|  +----------+    Picking Sortie    +----------+    Picking Entree   +------+ |
|  |          | ------------------> |          | -----------------> |       | |
|  | SOURCE A |       (Envoi)       | TRANSIT  |    (Reception)     | DEST B| |
|  |          | <------------------ |          |                    |       | |
|  +----------+  Retour Expediteur  +----------+                    +-------+ |
|                                         |                                    |
|                                         | Ajustement                         |
|                                         v Inventaire                         |
|                                   +----------+                               |
|                                   |  PERTE   |                               |
|                                   |INVENTAIRE|                               |
|                                   +----------+                               |
|                                                                              |
+-----------------------------------------------------------------------------+
```

### Types de Mouvements

| Mouvement | Source | Destination | Declencheur |
|-----------|--------|-------------|-------------|
| Envoi | Stock A | Transit | Bouton "Envoyer" |
| Reception | Transit | Stock B | Bouton "Terminer" ou "Reception Partielle" |
| Retour Expediteur | Transit | Stock A | Traitement reliquat |
| Ajustement Inventaire | Transit | Perte Inventaire | Traitement reliquat |

---

## 5. Tableau Recapitulatif des Scenarios

| Scenario | Demande | Envoye | Recu | Reliquat | Action | Stock A | Stock B |
|----------|---------|--------|------|----------|--------|---------|---------|
| Complet | 100 | 100 | 100 | 0 | - | 0 | 100 |
| Partiel + Retour | 100 | 100 | 70 | 30 | Retour | 30 | 70 |
| Partiel + Perte | 100 | 100 | 70 | 30 | Ajustement | 0 | 70 |
| Partiel + Report | 100 | 100 | 70 | 30 | Reporter | 0* | 70 |
| Envoi partiel | 100 | 80 | 80 | 0 | - | 0 | 80 |
| Annulation | 100 | 0 | 0 | 0 | Annuler | 100 | 0 |

*\* 30 unites restent en transit jusqu'au nouveau transfert*

---

## 6. Formules de Calcul

| Champ | Formule | Description |
|-------|---------|-------------|
| Reliquat | `qty_sent - qty_received` | Quantite non recue |
| Quantite en Transit | `qty_sent - qty_received` | Produits dans l'emplacement transit |
| Maximum Recevable | `qty_sent - qty_already_received` | Limite de reception |

---

## 7. Roles et Permissions

| Role | Groupe | Actions Autorisees |
|------|--------|-------------------|
| Demandeur | `group_stock_transfer_requester` | Creer, Soumettre, Recevoir |
| Validateur | `group_stock_transfer_validator` | Approuver, Annuler, Toutes actions |

---

## 8. Cas d'Utilisation Typiques

### Cas 1: Transfert de reapprovisionnement
Un magasin B demande des produits a l'entrepot central A.
- Workflow standard avec reception complete.

### Cas 2: Transfert avec casse en transport
Des produits sont endommages pendant le transport.
- Reception partielle + Ajustement inventaire pour la perte.

### Cas 3: Transfert avec erreur de comptage
L'expediteur a envoye moins que prevu.
- Reception partielle + Retour expediteur (les produits n'etaient pas dans le colis).

### Cas 4: Livraison en plusieurs fois
Le transporteur livre en deux voyages.
- Premiere reception partielle.
- Deuxieme reception partielle (ou complete) pour finaliser.

---

## 9. Notes Techniques

### Emplacement Transit
- Type: `transit`
- Partage entre societes (company_id = False)
- Reference: `stock.stock_location_inter_wh`

### Pickings Generes
Pour chaque transfert approuve, deux pickings sont crees:
1. **Picking Sortie**: Source -> Transit
2. **Picking Entree**: Transit -> Destination

### Transferts Inter-Societes
Si `source_company_id != dest_company_id`:
- Picking Sortie: Type `outgoing`
- Picking Entree: Type `incoming`

---

## 10. Support

Pour toute question ou assistance:
- **Email**: info@adicops.com
- **Site Web**: https://adicops-dz.com

---

*Document genere le 2025-12-10*
*Version: 1.0*
