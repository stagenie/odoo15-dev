# -*- coding: utf-8 -*-
{
    'name': 'Exclure Paiements du Rapprochement Factures',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Permet d\'exclure certains paiements de la proposition de rapprochement sur les factures',
    'description': """
Exclure Paiements du Rapprochement Factures
=============================================

Ce module ajoute une option sur les paiements et les écritures comptables
pour les exclure de la proposition automatique de rapprochement affichée
en bas des factures.

Cas d'usage :
- Soldes initiaux à ne pas rapprocher automatiquement
- Paiements réservés pour d'autres usages
- Avances à conserver non affectées

Fonctionnalités :
- Case à cocher "Ne pas proposer pour régler les factures" sur les paiements
- Case à cocher sur les lignes d'écritures comptables (receivable/payable)
- Filtre dans la vue liste des paiements
- L'option est modifiable à tout moment pour remettre le paiement en proposition
    """,
    'author': 'ADI Development',
    'website': 'https://www.adidev.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adi_account_payment_exclude/static/src/js/account_payment_exclude.js',
        ],
        'web.assets_qweb': [
            'adi_account_payment_exclude/static/src/xml/account_payment_exclude.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
