# Module Exclusion de Factures du Partner Ledger

## Description

Ce module Odoo 15 permet d'exclure certaines factures spécifiques du calcul des soldes clients/fournisseurs dans le rapport Partner Ledger (Grand livre des partenaires).

## Fonctionnalités

### Exclusion Sélective de Factures

- **Champ booléen** : Ajout d'un champ "Exclure du Partner Ledger" sur toutes les factures (clients et fournisseurs)
- **Exclusion automatique** : Les factures marquées sont automatiquement exclues des calculs du Partner Ledger
- **Compatible** : Fonctionne avec le module `accounting_pdf_reports` (Odoo Mates)
- **Traçabilité** : Le champ est tracké pour suivre les modifications

### Interface Utilisateur

- Le champ est visible dans :
  - Le formulaire des factures clients
  - Le formulaire des factures fournisseurs
  - La vue liste des factures (colonne optionnelle)

## Installation

### Prérequis

- Odoo 15
- Module `account` (installé par défaut)
- Module `accounting_pdf_reports` (présent dans `adi_third_party/adi_third_party1`)

### Installation du Module

1. Placer le module dans le répertoire `adi_dev/adi_dev1/`
2. Mettre à jour la liste des applications dans Odoo
3. Rechercher "Exclusion de Factures du Partner Ledger"
4. Cliquer sur "Installer"

## Utilisation

### Exclure une Facture du Partner Ledger

1. Ouvrir une facture client ou fournisseur
2. Cocher la case "Exclure du Partner Ledger"
3. Enregistrer la facture

### Générer le Rapport Partner Ledger

1. Aller dans Comptabilité → Rapports → Partner Ledger
2. Sélectionner les critères de filtrage
3. Générer le rapport
4. Les factures marquées comme "Exclure du Partner Ledger" ne seront pas incluses dans les calculs des soldes

## Détails Techniques

### Modèles Modifiés

#### `account.move`
- **Nouveau champ** : `exclude_from_partner_ledger` (Boolean)
  - Par défaut : `False`
  - Traçable : `True`
  - Aide : "Si coché, cette facture sera exclue du calcul des soldes dans le rapport Partner Ledger"

#### `report.accounting_pdf_reports.report_partnerledger`
- **Méthode héritée** : `_lines()`
  - Ajoute une clause SQL pour filtrer les factures exclues
  - Clause : `AND (m.exclude_from_partner_ledger IS NULL OR m.exclude_from_partner_ledger = FALSE)`

- **Méthode héritée** : `_sum_partner()`
  - Ajoute la même clause pour le calcul des totaux
  - Garantit la cohérence entre les lignes et les totaux

### Vues Modifiées

- `account.view_move_form` : Formulaire facture client
- `account.view_invoice_tree` : Liste des factures
- `account.view_in_invoice_bill_form` : Formulaire facture fournisseur

## Cas d'Usage

### Exemple 1 : Factures Litigieuses

Si un client a des factures en litige qui ne doivent pas être comptabilisées dans le solde actuel, vous pouvez les marquer comme exclues du Partner Ledger.

### Exemple 2 : Factures Exceptionnelles

Pour des transactions exceptionnelles ou des factures d'ajustement qui ne doivent pas affecter le solde courant du partenaire.

### Exemple 3 : Factures en Attente de Validation

Des factures en attente de validation finale qui ne doivent pas encore apparaître dans les rapports de solde.

## Compatibilité

- **Odoo Version** : 15.0
- **Modules compatibles** :
  - `accounting_pdf_reports`
  - `tis_partner_ledger_filter_balance`

## Support

Pour toute question ou problème :
- **Email** : info@adicops.com
- **Website** : https://adicops-dz.com

## Licence

LGPL-3

## Auteur

**ADICOPS**
- Website: https://adicops-dz.com
- Email: info@adicops.com

## Historique des Versions

### Version 15.0.1.0.0
- Première version
- Ajout du champ d'exclusion sur les factures
- Héritage du rapport Partner Ledger pour filtrer les factures exclues
- Vues pour l'interface utilisateur
