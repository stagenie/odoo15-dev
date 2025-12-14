# -*- coding: utf-8 -*-
{
    'name': 'Tableau de Bord Trésorerie',
    'version': '15.0.1.1.0',
    'category': 'Accounting/Treasury',
    'summary': 'Tableau de bord pour visualiser les soldes des caisses et banques',
    'description': """
Tableau de Bord Trésorerie
==========================

Ce module ajoute un tableau de bord visuel pour la trésorerie:

* Affichage des caisses avec leurs soldes
* Affichage des banques avec leurs soldes
* Total Caisses
* Total Banques
* Interface avec couleurs Bootstrap

Note: Pour les coffres et le Total Général, installez le module
adi_treasury_dashboard_extended.
    """,
    'author': 'ADI',
    'website': '',
    'depends': [
        'adi_treasury',
        'adi_treasury_bank',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/treasury_bank_views_ext.xml',
        'views/treasury_dashboard_views.xml',
        'views/treasury_dashboard_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adi_treasury_dashboard/static/src/scss/dashboard.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
