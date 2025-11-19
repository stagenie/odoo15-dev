# Module Gestion de Trésorerie Bancaire (adi_treasury_bank)

## Vue d'ensemble
Extension du module de trésorerie Odoo pour gérer complètement les comptes bancaires, opérations bancaires et transferts bidirectionnels entre banque, caisse et coffre-fort.

---

## 1️⃣ Comptes Bancaires (Treasury Bank)

### Qu'est-ce que c'est ?
Représentation virtuelle de vos comptes bancaires réels dans Odoo, avec suivi en temps réel des soldes.

### Informations clés
- **Code** : Identifiant unique du compte
- **Journal Bancaire** : Lié à un journal comptable de type "bank"
- **Données bancaires** : IBAN, BIC, numéro de compte, agence
- **Devise** : Multi-devises supportée
- **Responsable** : Utilisateur principal + liste d'utilisateurs autorisés

### Soldes disponibles
| Solde | Description |
|-------|-------------|
| **Solde Actuel** | Basé sur les écritures comptables |
| **Solde Physique** | Dernière clôture bancaire confirmée |
| **Découvert autorisé** | Limite définissable par compte |
| **Solde disponible** | Actuel - Découvert autorisé |

### Comment ça marche ?
1. Créer un compte bancaire : Menu **Trésorerie > Comptes Bancaires**
2. Relier un journal comptable existant
3. Entrer les infos bancaires (IBAN, BIC, etc.)
4. Valider → Le compte est prêt à l'emploi

---

## 2️⃣ Opérations Bancaires (Treasury Bank Operations)

### Qu'est-ce que c'est ?
Enregistrement détaillé de chaque opération bancaire (entrée/sortie) avec support des différentes méthodes de paiement.

### Types d'opérations
- **Virements** : Paiements électroniques
- **Chèques** : Émis ou encaissés
- **Cartes Bancaires** : Paiements par carte
- **Prélèvements** : Paiements récurrents
- **Frais Bancaires** : Commissions et intérêts
- **Autres** : Opérations personnalisées

### Dates importantes
| Date | Signification |
|------|---------------|
| **Date d'opération** | Quand l'opération s'est produite |
| **Date de valeur** | Quand l'argent est réellement crédité/débité (pour rapprochement) |

### États d'une opération
```
Brouillon → En attente → Validée → Clôturée
```

### Comment ça marche ?
1. Menu **Trésorerie > Opérations Bancaires** → **Créer**
2. Sélectionner le compte bancaire
3. Type : Entrée (in) ou Sortie (out)
4. Méthode de paiement (virement, chèque, etc.)
5. Montant et description
6. Valider l'opération

---

## 3️⃣ Transferts Bancaires (Étendus)

### Nouveaux types de transferts
Au-delà de la simple caisse ↔ caisse, le module supporte :

| Type de transfert | Sens | Description |
|------------------|------|-------------|
| **Banque → Caisse** | Retrait | Retrait d'espèces au guichet |
| **Caisse → Banque** | Dépôt | Remise d'espèces à la banque |
| **Banque → Coffre** | Retrait | Transfert en valeurs à sécuriser |
| **Coffre → Banque** | Dépôt | Mise en sécurité des valeurs |
| **Banque → Banque** | Virement | Inter-bancaire |

### Processus d'un transfert
```
1. Créer le transfert (Draft)
   ↓
2. Confirmer (Confirm)
   ↓
3. Effectuer (Done)
   ↓
4. Générer les opérations bancaires auto
```

### Informations de transfert bancaire
```
Méthode de paiement    : Virement/Chèque/etc.
Référence bancaire     : Numéro chèque, référence virement
Opération sortie       : Créée sur compte source
Opération entrée       : Créée sur compte destination
Soldes avant/après     : Affichés à titre informatif
```

### Comment créer un transfert ?
1. Menu **Trésorerie > Transferts**
2. **Créer** → Sélectionner type (ex: **Banque → Caisse**)
3. Compte source & destination
4. Montant
5. Ajouter méthode paiement & référence bancaire
6. **Confirmer** → **Effectuer**
7. ✅ Les opérations bancaires se créent automatiquement

---

## 4️⃣ Clôture Bancaire (Treasury Bank Closing)

### Qu'est-ce que c'est ?
Processus périodique de réconciliation entre vos relevés bancaires réels et Odoo.

### États de clôture
```
Brouillon → Confirmée → Validée → Archivée
```

### Étapes d'une clôture

#### 1️⃣ **Créer la clôture** (Draft)
- Menu : **Trésorerie > Clôtures Bancaires** → **Créer**
- Sélectionner compte bancaire
- Date de clôture
- Solde relevé bancaire (saisi manuellement)

#### 2️⃣ **Charger les opérations** (Draft)
- Bouton **"Recharger les opérations"**
- Récupère automatiquement toutes les opérations de la période
- Affiche liste détaillée avec dates de valeur

#### 3️⃣ **Confirmer** (Confirm)
- Vérifier l'écart : `Solde relevé - Solde théorique`
- Si écart = 0 : Parfait ! ✅
- Si écart ≠ 0 : Enquêter sur les différences
- Bouton **"Confirmer"**

#### 4️⃣ **Valider** (Validated)
- Crée automatiquement une opération d'ajustement si écart
- L'ajustement balance la différence
- Clôture figée, ne peut plus être modifiée
- Solde physique du compte = solde validé

### Réconciliation bancaire
```
Solde théorique    = Solde précédent + Entrées - Sorties
Solde relevé       = Relevé bancaire réel
Écart              = Solde relevé - Solde théorique

Si Écart ≠ 0  → Créer opération d'ajustement
```

### Comment faire une clôture ?
```
1. Aller à Trésorerie > Clôtures Bancaires
2. Créer > Sélectionner compte & date
3. Entrer solde du relevé bancaire
4. Charger opérations
5. Vérifier la liste
6. Si écart présent, l'enregistrer dans notes
7. Confirmer
8. Valider (crée ajustement auto si needed)
9. Archiver (optionnel)
```

---

## 5️⃣ Intégration Paiements Odoo

### Automatisations
- **Paiements Odoo** → **Opérations Bancaires** automatiquement
- Lors d'un paiement d'une facture :
  - Si journal = journal bancaire du compte
  - Une opération bancaire se crée automatiquement
  - Lien bidirectionnel maintenu

### Avantages
✅ Synchronisation automati que
✅ Moins d'erreurs manuelles
✅ Traçabilité complète
✅ Réconciliation plus rapide

---

## 6️⃣ Rapports et Exports

### Rapports disponibles
1. **Relevé de compte bancaire**
   - Soldes, transactions, écarts
   - Groupé par période

2. **Clôture bancaire détaillée**
   - Justification de chaque opération
   - Écart analysé

3. **État des comptes bancaires**
   - Vue synthétique multi-comptes
   - Soldes comparés (comptable vs physique)

### Comment imprimer ?
1. Ouvrir une clôture/compte bancaire
2. Bouton **"Imprimer"** (icône 🖨️)
3. Format PDF généré automatiquement

---

## 7️⃣ Sécurité & Contrôles

### Permissions
- **Groupe Treasury Bank User** : Lecture seule
- **Groupe Treasury Bank Manager** : Lecture/Écriture/Validation
- **Groupe Treasury Bank Auditor** : Lecture des clôtures validées

### Contrôles de validations
- ✅ Montants positifs obligatoires
- ✅ Compte bancaire requis
- ✅ Clôture précédente doit être validée
- ✅ Pas de modification après validation
- ✅ Limite découvert vérifiée au temps réel

---

## 📊 Workflow complet - Exemple

### Scénario : Transfert Caisse → Banque (Dépôt)

```
JOUR 1 : CRÉER LE TRANSFERT
┌─────────────────────────────────┐
│ Menu: Trésorerie > Transferts   │
│ Type: Caisse → Banque           │
│ Caisse source: Caisse Principale│
│ Compte dest: BNP Paribas        │
│ Montant: 5000 DZD              │
│ Méthode: Virement              │
│ Référence: REF-001             │
└─────────────────────────────────┘
         ↓ Confirmer
         ↓ Effectuer
         ↓
JOUR 1 : OPÉRATIONS AUTO
┌──────────────────────────────────────┐
│ Operation 1: Caisse -5000 (Sortie)   │
│ Operation 2: BNP +5000 (Entrée)      │
│ Status: Validées                     │
└──────────────────────────────────────┘

JOUR 5 : CLÔTURE BANCAIRE
┌───────────────────────────────────────┐
│ Compte: BNP Paribas                   │
│ Solde relevé bancaire: 125000 DZD     │
│ Solde théorique: 125000 DZD           │
│ Écart: 0 DZD ✅                       │
│ Confirmer → Valider                   │
└───────────────────────────────────────┘
```

---

## ❓ FAQ Rapide

### Q: Comment gérer plusieurs devises ?
**R:** Chaque compte bancaire a sa devise. Les opérations se font dans la devise du compte.

### Q: Que faire en cas d'écart à la clôture ?
**R:**
1. Vérifier les opérations en attente
2. Chercher opérations en double
3. Vérifier dates de valeur vs dates d'opération
4. Enregistrer l'écart (créé auto en ajustement)

### Q: Les transferts créent-ils les écritures comptables ?
**R:** OUI - Intégration complète avec la comptabilité Odoo (journal compte + contrepartie)

### Q: Peut-on modifier une opération validée ?
**R:** NON - Dès validation, l'opération est figée. Créer une opération inverse si correction nécessaire.

### Q: Comment tracker les responsabilités ?
**R:**
- Chaque compte = responsable principal
- Chaque opération = utilisateur créateur (tracking enabled)
- Clôture = signé par utilisateur validant

---

## 🚀 Raccourcis utiles

| Action | Accès rapide |
|--------|--------------|
| Créer opération | Trésorerie > Opérations > Créer |
| Faire transfert | Trésorerie > Transferts > Créer |
| Clôturer compte | Trésorerie > Clôtures > Créer |
| Voir soldes | Trésorerie > Comptes Bancaires (liste) |
| Imprimer relevé | Clôture ouverte → Imprimer |

---

## 📧 Support
Module développé par **ADICOPS**
Site : https://www.adicops.com
Email : info@adicops.com

**Version** : 15.0.1.0.0
**Licence** : LGPL-3
