# -*- coding: utf-8 -*-
{
    'name': 'ADI - Stock Manager Access',
    'version': '15.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Permet au Stock Manager de gérer les entrepôts, emplacements et accéder à la valeur inventaire',
    'description': """
ADI - Stock Manager Access
==========================

Ce module permet à l'administrateur de stock (Stock Manager) de:
- Créer et gérer les entrepôts (stock.warehouse)
- Créer et gérer les emplacements (stock.location)
- Accéder au menu Configuration Warehouse sans être administrateur système
- Accéder à la valeur inventaire (Inventory Valuation)

Fonctionnalités:
----------------
* Accès complet aux entrepôts pour le stock manager
* Accès complet aux emplacements pour le stock manager
* Menu direct pour la gestion des entrepôts et emplacements
* Accès à la valeur inventaire dans les rapports
    """,
    'author': 'ADI',
    'website': '',
    'depends': ['stock', 'stock_account'],
    'data': [
        'security/stock_manager_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
