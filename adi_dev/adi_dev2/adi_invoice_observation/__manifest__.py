# -*- coding: utf-8 -*-
{
    'name': 'Observation Facture',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Ajoute un champ observation sur les factures',
    'description': """
Observation Facture
===================
Ce module ajoute un champ "Observation" sur les factures client et fournisseur.

Le champ est visible sur:
- Le formulaire de la facture
- La liste des factures (colonne optionnelle)

Le champ n'apparait PAS sur les impressions de factures.
    """,
    'author': 'ADI',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
