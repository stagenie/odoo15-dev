# -*- coding: utf-8 -*-
{
    'name': 'ADI Payment Shortcuts',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Raccourcis rapides pour les paiements clients et fournisseurs',
    'description': """
ADI Payment Shortcuts
=====================
Ce module ajoute deux applications raccourcis dans le menu principal :
- Paiements Clients : Accès direct aux paiements de type client
- Paiements Fournisseurs : Accès direct aux paiements de type fournisseur
    """,
    'author': 'ADI',
    'website': '',
    'depends': ['account'],
    'data': [
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
