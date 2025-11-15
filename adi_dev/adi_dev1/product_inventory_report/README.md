# Rapport Inventaire Produits par Emplacement

## Description

Ce module Odoo 15 permet de générer un rapport d'inventaire détaillé affichant les quantités de produits par emplacement de stock. Il ajoute également l'affichage du partenaire (client/fournisseur) dans les vues de mouvements de stock.

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

- **Amélioration des mouvements de stock** :
  - Ajout d'une colonne "Partenaire" dans les vues de mouvements de stock
  - Affichage automatique du client ou fournisseur associé au mouvement
  - Récupération du partenaire depuis le picking ou les emplacements partenaires
  - Disponible dans toutes les vues tree des mouvements (standard, opérations, détaillées)

## Installation

1. Copier le module dans le répertoire addons d'Odoo
2. Mettre à jour la liste des applications
3. Installer le module "Rapport Inventaire Produits par Emplacement"

## Utilisation

### Rapport d'inventaire

1. Aller dans **Inventaire > Rapports > Rapport Inventaire Produits**
2. Sélectionner les filtres souhaités :
   - Catégories (optionnel)
   - Entrepôts (optionnel)
   - Emplacements (optionnel)
   - Cocher "Uniquement produits en stock" si nécessaire
3. Choisir le type de rapport (Écran ou PDF)
4. Cliquer sur "Générer le rapport"

### Affichage du partenaire dans les mouvements de stock

1. Aller dans **Inventaire > Rapports > Mouvements de Stock**
2. La colonne "Partenaire" est maintenant disponible et affiche automatiquement le client ou fournisseur associé
3. Vous pouvez afficher/masquer cette colonne via les options de la vue (icône ⚙️)

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
