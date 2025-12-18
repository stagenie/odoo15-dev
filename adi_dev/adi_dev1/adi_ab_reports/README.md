# Module ADI AB Reports - Rapports Personnalisés pour AB Energie

## Description

Ce module personnalise tous les rapports de vente et facturation pour AB Energie selon les spécifications suivantes :

## Fonctionnalités

### 1. Devis
- **Supprimé** : Échéance, colonne TVA, colonne Remise
- **Modifié** : Affichage du Montant TTC dans les lignes au lieu du HT
- **Ajouté** : "Offre valable jusqu'au" en bas
- **Total** : Affiche uniquement "Net à payer" (TTC)

### 2. Proforma
- **Supprimé** : Échéance en haut
- **Conservé** : Total HT et TVA
- **Modifié** : "Total" renommé en "Net à payer"
- **Ajouté** : "Offre valable jusqu'au" en bas

### 3. Bon de commande
- **Supprimé** : Colonne TVA, montants HT et TVA en bas
- **Conservé** : Colonne remise et total remise
- **Modifié** : Affichage du Total TTC dans les lignes
- **Ajouté** :
  - Délais de livraison (date)
  - Modalités de paiement (texte éditable, par défaut: 50% 30% 20%)
  - "Net à payer" (Total TTC)

### 4. Bon de livraison
- **Modifié** : Titre "Bon de livraison"
- **Supprimé** : "Facture de vente", "Bon de livraison valorisé"

### 5. Facture
- **Supprimé** : Date échéance, Origine, titre "Facture"
- **Conservé** : Numéro de facture uniquement
- **Ajouté** : Mode de règlement en bas (Chèque N°/Date, Espèce/Date)
- **Modifié** : Affichage de la remise avec 2 décimales
- **Désactivé** : Impression "Journal Vente"

### 6. Bon de livraison valorisé (Vente BL)
- **Supprimé** : Date échéance, Origine, colonne TVA, colonne Remise
- **Modifié** : Affichage du Total TTC dans les lignes au lieu du HT
- **Total** : Affiche uniquement "Net à payer" (TTC)

## Installation

1. Ce module dépend de `sale_discount_total`
2. Installer le module via Apps > ADI AB Reports
3. Mettre à jour la liste des modules si nécessaire

## Utilisation

Les rapports sont automatiquement modifiés une fois le module installé.

Pour utiliser les nouveaux champs :
- **Délais de livraison** : À remplir dans le formulaire de bon de commande
- **Modalités de paiement** : Texte éditable dans le bon de commande
- **Offre valable jusqu'au** : Calculé automatiquement (30 jours par défaut)

## Compatibilité

- Odoo 15.0
- Module sale_discount_total requis
- Compatible avec adi_bank_payment_mode pour les modes de règlement
