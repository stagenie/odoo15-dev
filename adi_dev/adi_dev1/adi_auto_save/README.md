# Module Enregistrement Automatique (Auto-Save)

## Description

Ce module Odoo 15 permet l'enregistrement automatique des formulaires pour :
- **Devis / Bons de commandes** (sale.order)
- **Demandes d'achat / Commandes d'achat** (purchase.order)

## Fonctionnalités

- ✅ Sauvegarde automatique à intervalles réguliers configurables
- ✅ Notification discrète lors de chaque sauvegarde
- ✅ Configuration par module (ventes/achats)
- ✅ Activation/désactivation globale
- ✅ Ne sauvegarde que si le formulaire a été modifié
- ✅ Ne sauvegarde pas les nouveaux enregistrements non créés

## Configuration

1. Allez dans **Paramètres > Technique > Enregistrement Automatique**
2. Activez l'enregistrement automatique
3. Configurez l'intervalle de sauvegarde (en secondes, défaut: 30)
4. Choisissez les modules pour lesquels activer l'auto-save :
   - Devis/Bons de commandes
   - Demandes/Commandes d'achat

## Installation

1. Copiez le module dans votre répertoire addons
2. Mettez à jour la liste des applications
3. Installez le module "Enregistrement Automatique"

## Dépendances

- `sale_management`
- `purchase`

## Auteur

**ADICOPS**
- Email: info@adicops.com
- Website: https://adicops.com/

## Version

15.0.1.0.0

## Licence

LGPL-3
