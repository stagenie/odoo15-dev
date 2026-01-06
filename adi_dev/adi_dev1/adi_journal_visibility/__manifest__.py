# -*- coding: utf-8 -*-
{
    'name': 'ADI Journal Visibility',
    'version': '15.0.1.1.0',
    'summary': 'Masquer des journaux sans les archiver',
    'description': """
        Ce module permet de masquer des journaux comptables pour tous les utilisateurs
        sans avoir à les archiver.

        Fonctionnalités:
        - Champ "Masqué" sur les journaux
        - Les journaux masqués n'apparaissent pas dans les listes et sélections
        - Seuls les utilisateurs avec le droit "Voir journaux masqués" peuvent les voir
        - Alternative sûre à l'archivage
    """,
    'category': 'Accounting',
    'author': 'ADI',
    'website': '',
    'depends': [
        'account',
    ],
    'data': [
        'security/journal_visibility_security.xml',
        'security/ir.model.access.csv',
        'views/account_journal_views.xml',
        'views/account_payment_register_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
