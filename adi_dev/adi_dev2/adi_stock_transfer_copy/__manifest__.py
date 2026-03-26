# -*- coding: utf-8 -*-
{
    'name': 'ADI Stock Transfer - Duplication & Alerte Doublons',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Duplication complète des lignes de transfert et alerte articles redondants',
    'description': """
ADI Stock Transfer Copy
========================

Ce module corrige la duplication des transferts de stock et ajoute
une alerte visuelle pour les articles en double.

Fonctionnalités:
----------------
* Duplication complète des lignes de transfert (articles + quantités demandées)
* Remise à zéro des quantités envoyées/reçues sur le duplicata
* Nettoyage des allocations multi-source obsolètes
* Alerte non bloquante lors de la saisie d'articles redondants dans un transfert
    """,
    'author': 'ADICOPS',
    'website': 'https://www.adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'adi_stock_transfer_enhanced',
    ],
    'data': [
        'views/stock_transfer_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
