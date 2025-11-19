# -*- coding: utf-8 -*-
{
    'name': 'Gestion des Dépenses de Caisse',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Gestion des dépenses de caisse avec remboursements et avances',
    'description': """Module de Gestion des Dépenses de Caisse

Ce module étend adi_treasury pour gérer les dépenses de caisse :

Fonctionnalités :
- Gestion des remboursements (employé achète, justificatifs, validation)
- Gestion des avances de caisse (montant à l'employé, suivi solde, règlement)
- Comptes personnels (suivi solde, limite d'avance, historique)
- Intégrations complètes (trésorerie, RH, pièces justificatives)
""",
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'hr',
        'adi_treasury',
    ],
    'data': [
        'security/cash_expense_security.xml',
        'security/ir.model.access.csv',
        'data/cash_expense_data.xml',
        'views/cash_expense_views.xml',
        'views/cash_expense_line_views.xml',
        'views/personal_cash_account_views.xml',
        'views/cash_expense_menu.xml',
        'reports/cash_expense_report_templates.xml',
        'wizard/cash_expense_settlement_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
