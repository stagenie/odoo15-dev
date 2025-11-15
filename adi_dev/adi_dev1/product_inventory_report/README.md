# Rapport Inventaire Produits par Emplacement

## Description

Ce module Odoo 15 permet de générer un rapport d'inventaire détaillé affichant les quantités de produits par emplacement de stock.

## Fonctionnalités

- **Filtrage avancé** :
  - Par catégorie de produits
  - Par entrepôt
  - Par emplacements spécifiques
  - Option pour afficher uniquement les produits en stock

- **Affichage flexible** :
  - Affichage à l'écran avec vue tableau
  - Impression PDF
  - Option pour afficher/masquer les catégories
  - Support multi-emplacements et multi-entrepôts

- **Colonnes du rapport** :
  - Référence produit
  - Désignation
  - Catégorie (optionnel)
  - Quantité par emplacement (jusqu'à 10 emplacements)
  - Total des quantités

## Installation

1. Copier le module dans le répertoire addons d'Odoo
2. Mettre à jour la liste des applications
3. Installer le module "Rapport Inventaire Produits par Emplacement"

## Utilisation

1. Aller dans **Inventaire > Rapports > Rapport Inventaire Produits**
2. Sélectionner les filtres souhaités :
   - Catégories (optionnel)
   - Entrepôts (optionnel)
   - Emplacements (optionnel)
   - Cocher "Uniquement produits en stock" si nécessaire
3. Choisir le type de rapport (Écran ou PDF)
4. Cliquer sur "Générer le rapport"

## Exemple de rapport

```
Réf    | Désignation  | Catégorie      | Stock Principal | Zone A | Zone B | Total
-------|--------------|----------------|-----------------|--------|--------|-------
Dé3    | Table Bureau | Mobilier       | 4               | 4      | 5      | 13
CH01   | Chaise       | Mobilier       | 10              | 0      | 8      | 18
```

## Dépendances

- stock
- product

## Auteur

ADICOPS - https://adicops-dz.com

## Licence

LGPL-3
