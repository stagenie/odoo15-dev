# -*- coding: utf-8 -*-
{
    'name': 'Préservation Prix de Vente',
    'version': '15.0.1.0.0',
    'summary': 'Préserve le prix unitaire saisi manuellement lors de la modification des lignes de devis',
    'description': """
        Ce module empêche la réinitialisation automatique du prix unitaire
        lorsqu'on modifie la quantité ou la remise d'une ligne de devis/commande.

        Le prix saisi manuellement est préservé et ne sera plus écrasé par
        le prix de la liste de prix lors des modifications ultérieures.
    """,
    'category': 'Sales/Sales',
    'author': 'ADI',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
