# -*- coding: utf-8 -*-
{
    'name': 'Affichage Soldes Bancaires (Rapproché/Non Rapproché)',
    'version': '15.0.2.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Affiche les soldes rapprochés et non rapprochés des banques et du tableau de bord',
    'description': """
Affichage des Soldes Bancaires Détaillés
========================================

Ce module ajoute l'affichage des soldes bancaires détaillés :

* **Solde Actuel** : Toutes les opérations validées
* **Solde Rapproché** : Uniquement les opérations pointées avec le relevé bancaire
* **Solde Non Rapproché** : Opérations en attente de pointage

Ces informations sont affichées dans :
- La vue Kanban des comptes bancaires
- Le formulaire des comptes bancaires
- Le tableau de bord de trésorerie (avec totaux)

Configuration :
- Paramètre pour activer/désactiver l'affichage des détails de rapprochement
    """,
    'author': 'ADI Dev',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'adi_treasury_bank',
        'adi_treasury_dashboard',
        'adi_treasury_dashboard_extended',  # Pour que notre init() soit appelé en dernier
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/treasury_bank_views.xml',
        'views/treasury_dashboard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
