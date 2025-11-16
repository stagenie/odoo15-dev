# -*- coding: utf-8 -*-

{
    'name': "Plan comptable - SCF Algérien",
    'category': 'Accounting/Localizations/Account Charts',
    'summary': """ Plan comptable normalisé - Système Comptable Financier Algérien - odoo 14 """,
    "contributors": [
        "1 <Nassim REFES>",
    ],
    'sequence': 1,
    'version': '15.0.1.0',
    "license": "LGPL-3",
    'author': 'DevNationSolutions',
    'website': 'https://devnation-solutions.com/',
    "price": 4.99,
    "currency": 'EUR',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'data/l10n_dz_scf_chart_data.xml',
        'data/account_group.xml',
        'data/account_account_template_data.xml',
        'data/account_chart_template_data.xml',
        'data/account_data.xml',
        'data/account_tax_data.xml',
        'data/account_fiscal_position_template_data.xml',
        'data/account_chart_template_configure_data.xml',

        'views/account_account.xml',
        'views/account_group.xml',

        'security/ir.model.access.csv',
    ],
    'images': ['images/main_screenshot.gif'],

    'post_init_hook': 'post_init_hook',

    'installable': True,
    'auto_install': False,
    'application':False,
}