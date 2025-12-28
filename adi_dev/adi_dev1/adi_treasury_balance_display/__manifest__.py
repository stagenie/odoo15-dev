# -*- coding: utf-8 -*-
{
    'name': 'Affichage Soldes Bancaires (Rapproché/Non Rapproché)',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Affiche les soldes rapprochés et non rapprochés des banques',
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
    """,
    'author': 'ADI Dev',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'adi_treasury_bank',
    ],
    'data': [
        'views/treasury_bank_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
