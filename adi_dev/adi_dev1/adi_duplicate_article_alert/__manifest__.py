# -*- coding: utf-8 -*-
{
    'name': 'Alerte Article en Double',
    'version': '15.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Alerte lors de la saisie en double d\'un article',
    'description': """
        Module d'alerte pour les articles en double :
        - Alerte dans les Devis / Bons de commande (Vente)
        - Alerte dans les Demandes de prix / Bons de commande (Achat)
        - Alerte dans les Factures clients et fournisseurs
        - Alerte dans les Bons de livraison / Réception

        L'alerte est non bloquante et permet de continuer la saisie.
    """,
    "author": "ADICOPS",
    "email": 'info@adicops.com',
    "website": 'https://adicops.com/',
    'depends': ['sale_management', 'purchase', 'account', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
