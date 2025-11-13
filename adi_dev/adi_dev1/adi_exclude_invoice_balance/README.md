# Module Exclusion Factures du Solde Partenaire

## Description

Ce module permet d'exclure certaines factures et avoirs du calcul des soldes clients/fournisseurs dans Odoo 15.

## Fonctionnalités

- Ajout d'un champ booléen "Exclure du solde partenaire" sur les factures et avoirs
- Les factures/avoirs marqués ne sont pas inclus dans le calcul des soldes (crédit, débit, balance)
- Impact sur les rapports Partner Ledger
- Impact sur les vues comptables
- Par défaut, toutes les factures sont incluses dans les calculs
- Compatible avec les modules de comptabilité tiers

## Utilisation

### Marquer une facture/avoir comme exclus du solde

1. Ouvrir une facture client/fournisseur ou un avoir
2. Cocher la case "Exclure du solde partenaire"
3. Enregistrer la facture

La facture ne sera plus prise en compte dans le calcul du solde du partenaire.

### Filtres disponibles

Dans la liste des factures, vous pouvez utiliser les filtres suivants :
- "Exclues du solde" : affiche uniquement les factures exclues du calcul
- "Incluses au solde" : affiche uniquement les factures incluses dans le calcul
- Grouper par "Exclusion du solde"

## Impact technique

### Modèles modifiés

1. **account.move** : Ajout du champ `exclude_from_partner_balance`
2. **account.move.line** : Ajout du champ `exclude_from_partner_balance` avec héritage automatique depuis account.move
3. **res.partner** : Modification des méthodes de calcul des soldes :
   - `_credit_debit_get()` : exclut les lignes marquées
   - `_asset_difference_search()` : exclut les lignes marquées dans les recherches

### Calculs affectés

Les calculs suivants excluent maintenant les factures marquées :
- Crédit total (Total Receivable)
- Débit total (Total Payable)
- Solde partenaire (Balance)
- Recherches sur les soldes
- Rapports Partner Ledger

## Installation

1. Copier le module dans le répertoire des addons Odoo
2. Mettre à jour la liste des modules
3. Installer le module "Exclusion Factures du Solde Partenaire"

## Configuration

Aucune configuration requise. Le module est prêt à l'emploi après installation.

## Auteur

**ADICOPS**
- Email: info@adicops.com
- Website: https://adicops.com/

## Version

15.0.1.0.0

## Licence

AGPL-3
