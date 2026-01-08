# -*- coding: utf-8 -*-
{
    'name': 'ADI Fournisseurs de Service',
    'version': '15.0.1.3.0',
    'summary': 'Gestion des fournisseurs de service',
    'description': """
        Ce module permet de:
        - Marquer un fournisseur comme "Fournisseur de Service"
        - Menu dédié pour les Fournisseurs de Service
        - Menu dédié pour les Factures Fournisseurs de Service
        - Factures Service avec filtrage automatique:
          * Fournisseurs: uniquement les fournisseurs de service
          * Articles: uniquement les articles de type service
        - Masque le bouton "ADD MULTIPLE PRODUCTS" sur les factures service
    """,
    'category': 'Accounting',
    'author': 'ADI',
    'website': '',
    'depends': [
        'base',
        'account',
        'purchase',
        'product',
        'bi_multi_product_selection',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/bi_multi_product_hide.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
