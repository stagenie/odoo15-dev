# Module Gestion des Dépenses de Caisse (adi_cash_expense)

## Vue d'ensemble
Extension du module de trésorerie Odoo pour gérer complètement les dépenses de caisse des employés, incluant remboursements et avances avec suivi par compte personnel.

---

## 1️⃣ Dépenses de Caisse (Cash Expense)

### Qu'est-ce que c'est ?
Enregistrement d'une dépense associée à un employé, avec deux types principaux :

#### Type 1: Remboursement 💰
L'employé a **déjà payé** avec ses propres fonds et doit être **remboursé** par l'entreprise.

**Exemple**: Employé achète du matériel, on le rembourse

#### Type 2: Avance 📋
L'entreprise donne un **montant à l'avance** à l'employé qui doit dépenser et justifier.

**Exemple**: On donne 5000 DZD à l'employé pour un voyage, il dépense et rend la différence

### Informations clés d'une dépense

| Champ | Obligatoire? | Description |
|-------|-------------|-------------|
| **Référence** | ✅ | Généré auto (DEP/YYYY/00001) |
| **Date** | ✅ | Date de la dépense |
| **Type** | ✅ | Remboursement ou Avance |
| **Employé** | ✅ | Bénéficiaire |
| **Département** | ❌ | Affectation comptable |
| **Caisse** | ✅ | Caisse d'où sort l'argent |
| **Montant** | ✅ | Automatique (somme des lignes) |
| **Description** | ✅ | Motif de la dépense |
| **Justificatifs** | ✅ | Factures, reçus, etc. |

### États d'une dépense

```
Brouillon → Soumis → Approuvé → Payé → Réglé
  (draft)  (submit) (approved) (paid) (settled)
    ↓
  Annulé (cancel)
```

#### États détaillés:

| État | Qui peut? | Action suivante |
|------|----------|-----------------|
| **Brouillon** | Créateur | Soumettre ou Annuler |
| **Soumis** | Approbateur | Approuver ou Rejeter |
| **Approuvé** | Caissier | Payer (créer opération caisse) |
| **Payé** | Système | Réglé automatiquement (pour avances) |
| **Réglé** | - | État final (avances) |
| **Annulé** | Gestionnaire | Irrévocable |

### Lignes de dépense (Détail)

Chaque dépense peut avoir **plusieurs lignes** pour plus de clarté :

| Champ | Type | Exemple |
|-------|------|---------|
| Article | Optional | Laptop |
| Description | Obligatoire | Achat ordinateur portable |
| Quantité | Obligatoire | 1 |
| Prix unitaire | Obligatoire | 50000 DA |
| **Sous-total** | Auto | 50000 DA |

**Calcul automatique** : `Sous-total = Quantité × Prix unitaire`

Le **montant total** de la dépense = **Somme de tous les sous-totals**

### Exemple complet : Remboursement

```
📄 Dépense de Caisse
─────────────────────────
Référence: DEP/2025/00042
Date: 15/01/2025
Type: REMBOURSEMENT
Employé: Ahmed MARTIN
Département: Logistique
Caisse: Caisse Principale
État: Brouillon

📋 Lignes de détail:
─────────────────────────
1. Fournitures de bureau      Qty: 1  Prix: 2500 DA  =  2500 DA
2. Papier A4 (5 ramettes)    Qty: 5  Prix: 300 DA   =  1500 DA
3. Encres d'imprimante        Qty: 3  Prix: 1200 DA =  3600 DA

📊 TOTAL: 7600 DA
```

---

## 2️⃣ Comptes Personnels (Personal Cash Account)

### Qu'est-ce que c'est ?
Suivi **par employé** de :
- ✅ Solde des avances en cours
- ✅ Total des avances reçues
- ✅ Total des remboursements
- ✅ Limite d'avance autorisée

### Informations clés

| Info | Description |
|------|-------------|
| **Employé** | Identifiant unique |
| **Solde actuel** | Avances données - dépensées |
| **Limite d'avance** | Montant max autorisé (0 = pas de limite) |
| **Avances en cours** | Nombre d'avances payées non réglées |
| **Total avances** | Somme de toutes les avances reçues |
| **Total remboursements** | Somme de tous les remboursements |

### Comment ça fonctionne ?

```
Création dépense "Avance"
         ↓
   Montant: 5000 DA
   État: Brouillon
         ↓
   Approuvé
         ↓
   Payé (opération caisse créée)
   Solde compte: +5000 DA (avance donnée)
         ↓
Employé dépense 3500 DA
   amount_spent = 3500 DA
   Solde restant = 5000 - 3500 = 1500 DA
         ↓
   RÉGLER avance → Employé retourne 1500 DA
   État: Réglé
   Solde compte: 0 DA
```

### Filtres disponibles

| Filtre | Affiche |
|--------|---------|
| **Avec avances en cours** | Comptes avec avances payées non réglées |
| **Avec solde** | Comptes avec solde > 0 |

---

## 3️⃣ Workflow Complet

### Scénario 1: Remboursement Simple

```
1️⃣ CRÉER
   Menu: Trésorerie > Dépenses de Caisse > Créer
   Type: REMBOURSEMENT
   Employé: Fatima DURAND
   Montant: 2500 DA
   Description: Repas client
   Caisse: Caisse Principale
   État: Brouillon

2️⃣ AJOUTER DÉTAILS
   Ligne 1: Repas restaurant "Alfredo"  → 2500 DA
   Pièces jointes: Facture restaurant (PDF)

3️⃣ SOUMETTRE
   Bouton: "Soumettre"
   État: Soumis
   Notification: Approbateur averti

4️⃣ APPROUVER (Approbateur)
   Bouton: "Approuver"
   État: Approuvé
   Montant validé: 2500 DA

5️⃣ PAYER (Caissier)
   Bouton: "Payer"
   ✅ Opération caisse créée auto
   ✅ Caisse débite de 2500 DA
   État: Payé
   Signature: Caissier qui a payé
   Date: Automatique

6️⃣ FIN
   État: Payé (Terminal pour remboursement)
   Historique complet dans "Opérations"
```

### Scénario 2: Avance avec Règlement

```
1️⃣ CRÉER AVANCE
   Type: AVANCE
   Employé: Hassan MOROCCO
   Montant: 10000 DA
   Raison: Voyage à Alger
   État: Brouillon

2️⃣ APPROUVER & PAYER
   ✅ Approuvé
   ✅ Payé (opération caisse créée)
   Compte personnel Hassan:
   - Solde: +10000 DA
   - Avances en cours: 1
   État: Payé (EN ATTENTE DE RÈGLEMENT)

3️⃣ EMPLOYÉ DÉPENSE
   Dépense réelle: 8500 DA (essence, hôtel, etc.)
   amount_spent = 8500 DA
   Solde restant = 10000 - 8500 = 1500 DA

4️⃣ RÉGLER L'AVANCE (Wizard)
   Menu: Bouton "Régler avance"
   Montant avancé: 10000 DA ✓ Pré-rempli
   Montant dépensé: 8500 DA  ← Entrer montant réel
   ↓ Calcul auto:
   À retourner: 1500 DA (Hassan rend l'argent non dépensé)

   Justificatifs: Reçus, factures
   Notes: "Déplacement réussi"

   Bouton: "Régler"
   ✅ Opération caisse créée (entrée de 1500 DA)
   État: Réglé
   Compte Hassan: Solde = 0 DA

5️⃣ FIN
   Historique complet:
   - Dépense initiale: Payé
   - Dépense réglée: Réglé
   - Caisse: +10000 DA → -1500 DA = +8500 DA net
```

---

## 4️⃣ Workflow de Règlement (Wizard)

### Qu'est-ce que c'est ?
Boîte de dialogue pour finaliser une **avance** en enregistrant les dépenses réelles.

### Champs du Wizard

| Champ | Type | Remplissage |
|-------|------|-------------|
| **Employé** | Affichage | Pré-rempli (lecture seule) |
| **Caisse** | Affichage | Pré-remplie (lecture seule) |
| **Montant avancé** | Affichage | 10000 DA (pré-rempli) |
| **Montant dépensé** | Saisie | 8500 DA (à entrer par utilisateur) |
| **À retourner** | Calc auto | = Montant avancé - Montant dépensé |
| **À payer supplémentaire** | Calc auto | Si montant dépensé > montant avancé |
| **Justificatifs** | Upload | Pièces jointes supplémentaires |
| **Notes** | Texte | Commentaires sur le règlement |

### Logique de Calcul

```
Si Montant dépensé < Montant avancé:
  → À RETOURNER = Montant avancé - Montant dépensé
  → Opération caisse ENTRÉE (l'employé rend)

Si Montant dépensé = Montant avancé:
  → Montant exact dépensé ✅
  → Pas d'opération supplémentaire

Si Montant dépensé > Montant avancé:
  → À PAYER SUPPLÉMENTAIRE = Montant dépensé - Montant avancé
  → Opération caisse SORTIE (on paie plus)
```

---

## 5️⃣ Intégration Trésorerie

### Opérations de Caisse Auto-créées

Chaque dépense **payée** crée une **opération de caisse** :

| Type Dépense | Opération Créée | Type | Catégorie |
|-------------|-----------------|------|-----------|
| **Remboursement** | Sortie | OUT | REMB |
| **Avance** | Sortie | OUT | AVANC |
| **Retour d'avance** | Entrée | IN | RETAV |
| **Paiement supplémentaire** | Sortie | OUT | SUPPL |

### Exemple de Traçabilité

```
Dépense: DEP/2025/00042 (Remboursement 7600 DA)
              ↓
         Approuvée
              ↓
         Payée par: Caissier AHMED
              ↓
Opération créée:
  - Référence: DEP/2025/00042
  - Type: Sortie (OUT)
  - Montant: 7600 DA
  - Caisse: Caisse Principale
  - Catégorie: REMB (Remboursement employé)
  - Date: 15/01/2025 10:30
              ↓
       Impact Solde Caisse:
       Avant: 50000 DA
       Après: 42400 DA
```

---

## 6️⃣ Rapports

### Rapport: Bon de Dépense

**Accessible**: Ouvrir dépense → Bouton "Imprimer"

**Contient**:
- Type (Remboursement ou Avance)
- Employé & Département
- Détail des lignes
- Total montant
- Justificatifs liés
- Signatures (Approuvé par, Payé par)

**Format**: PDF téléchargeable

---

## 7️⃣ Sécurité & Permissions

### Groupes d'Accès

| Groupe | Permissions |
|--------|-------------|
| **User** | Lecture seule |
| **Manager** | Lecture/Écriture/Approbation |
| **Accountant** | Paiement des dépenses |
| **Admin** | Tous les accès |

### Contrôles Validations

✅ Montants positifs obligatoires
✅ Employé requis
✅ Caisse obligatoire
✅ Pas de modification après paiement
✅ Justificatifs encouragés
✅ Limite avance vérifiée si définie

---

## 📊 Tableaux de Bord Statistiques

### Sur le Compte Personnel

```
┌─────────────────────────────┐
│ COMPTE: Ahmed MARTIN        │
├─────────────────────────────┤
│ Avances en cours:    2      │
│ Total avances:  25000 DA    │
│ Total remboursements: 5200 DA│
│ Solde actuel:    3500 DA    │
│ Limite d'avance:  50000 DA  │
└─────────────────────────────┘
```

### Statistiques par Dépense

Affichées dans les détails:
- ✅ Nombre de pièces jointes
- ✅ Opérations de caisse liées
- ✅ Compte personnel de l'employé
- ✅ Dates (création, approbation, paiement, règlement)

---

## 🔄 Workflow Résumé (Diagramme)

```
           REMBOURSEMENT                      AVANCE
           ────────────                      ──────

         Brouillon (Draft)                  Brouillon (Draft)
             ↓ Soumettre                        ↓ Soumettre
         Soumis (Submitted)                 Soumis (Submitted)
             ↓ Approuver                        ↓ Approuver
         Approuvé (Approved)                Approuvé (Approved)
             ↓ Payer                            ↓ Payer
         Payé (Paid) ✓ TERMINAL               Payé (Paid)
         [FIN]                                  ↓ Employé dépense & règle
                                           Réglé (Settled) ✓ TERMINAL
                                               [FIN]

         ❌ Annuler → Annulé (Cancel) - À tout moment
```

---

## 📋 Checklist Installation

- [x] Module installé ✅
- [ ] Séquences créées (DEP/YYYY/XXXXX)
- [ ] Catégories opérations créées (REMB, AVANC, RETAV, SUPPL)
- [ ] Caisses configurées
- [ ] Employés importés
- [ ] Permissions RH assignées
- [ ] Premier remboursement de test
- [ ] Premier règlement avance de test

---

## ❓ FAQ Rapide

### Q: Comment créer un remboursement ?
**R:** Trésorerie > Dépenses > Créer → Type: Remboursement → Ajouter lignes → Approuver → Payer

### Q: L'employé peut-il dépenser plus que l'avance ?
**R:** OUI - Système permet de payer supplémentaire. Lors du règlement, le montant extra est traité comme "À payer supplémentaire"

### Q: Où voir les dépenses d'un employé ?
**R:** Trésorerie > Comptes Personnels → Sélectionner employé → Voir toutes dépenses et avances

### Q: Comment tracker les justificatifs ?
**R:** Pièces jointes dans chaque dépense + Magasin de fichiers Odoo + Rapports avec scans

### Q: Les opérations de caisse se créent auto ?
**R:** OUI - Dès qu'on clique "Payer", une opération caisse est créée automatiquement avec la bonne catégorie

### Q: Peut-on modifier une dépense payée ?
**R:** NON - Figée après paiement. Créer une dépense d'ajustement si correction nécessaire

### Q: Limite d'avance = contrôle strict ?
**R:** C'est un contrôle de saisie. Si dépassement prévu, augmenter la limite avant de soumettre

---

## 🚀 Raccourcis utiles

| Action | Accès |
|--------|-------|
| Créer dépense | Trésorerie > Dépenses > Créer |
| Mes dépenses | Trésorerie > Dépenses > Filtre "Créé par moi" |
| À approuver | Trésorerie > Dépenses > Filtre "État: Soumis" |
| À payer | Trésorerie > Dépenses > Filtre "État: Approuvé" |
| Comptes employés | Trésorerie > Comptes Personnels |
| Statistiques | Comptes > Voir statistiques |

---

## 📧 Support
Module développé par **ADICOPS**
Site : https://adicops-dz.com
Email : info@adicops.com

**Version** : 15.0.1.0.0
**Licence** : LGPL-3
**Dépendances** : base, account, hr, adi_treasury
