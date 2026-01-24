# -*- coding: utf-8 -*-
{
    'name': 'ADI Journal Achat Service',
    'version': '15.0.1.0.0',
    'summary': 'Journaux d\'achat dédiés aux services',
    'description': """
        Ce module permet de:
        - Marquer un journal d'achat comme "Journal Service"
        - Filtrer automatiquement les journaux sur les factures fournisseur:
          * Factures Service: uniquement les journaux marqués "Service"
          * Factures normales: exclut les journaux marqués "Service"
        - Réduire les erreurs lors de la création de factures fournisseur
    """,
    'category': 'Accounting',
    'author': 'ADI',
    'website': '',
    'depends': [
        'account',
        'adi_service_supplier',
    ],
    'data': [
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
