# -*- coding: utf-8 -*-
{
    'name': 'Impression du Stock',
    'version': '15.0.1.0.4',
    'category': 'Inventory/Inventory',
    'summary': 'Permet d\'imprimer l\'état du stock avec différentes options de filtrage',
    'description': """
Impression du Stock
===================

Ce module permet d'imprimer un état du stock avec les options suivantes :

**Options d'impression:**
- Tous les produits (stockables)
- Tout le stock (quantité >= 0)
- Stock actuel uniquement (quantité > 0)

**Filtrage par catégories:**
- Toutes les catégories
- Catégories sélectionnées (avec leurs sous-catégories)

**Informations affichées:**
- Référence produit
- Désignation
- Unité de mesure
- Coût
- Prix de vente
- Quantité en stock
- Valeur au coût

**Totaux:**
- Nombre de produits
- Quantité totale
- Valeur totale au coût
- Valeur totale au prix de vente
    """,
    'author': 'ADI',
    'website': 'https://www.adi.com',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/stock_print_report.xml',
        'views/stock_print_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
