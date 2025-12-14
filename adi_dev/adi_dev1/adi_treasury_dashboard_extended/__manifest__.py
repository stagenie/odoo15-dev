# -*- coding: utf-8 -*-
{
    'name': 'Tableau de Bord Trésorerie - Extension Coffres',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Extension du tableau de bord avec les coffres et totaux avancés',
    'description': """
Tableau de Bord Trésorerie - Extension Coffres
===============================================

Ce module étend le tableau de bord de trésorerie avec:

* Affichage des coffres avec leurs soldes
* Total Coffres
* Total Général (Caisses + Banques + Coffres)
* Indicateurs de statut (Finalisé/En cours)
* Menu raccourci pour les coffres
    """,
    'author': 'ADI',
    'website': '',
    'depends': [
        'adi_treasury_dashboard',
    ],
    'data': [
        'views/treasury_dashboard_extended_views.xml',
        'views/treasury_dashboard_extended_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
