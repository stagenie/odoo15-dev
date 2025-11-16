# -*- coding: utf-8 -*-

{
    'name': "Rapports selon les normes algérienne",
    'category': 'DZ Reports',
    'summary': """ Rapports selon les normes algérienne - odoo 14 """,
    "contributors": [
        "1 <Nassim REFES>",
    ],
    'sequence': 1,
    'version': '15.0.1.0',
    "license": "OPL-1",
    'author': 'DevNationSolutions',
    'website': 'https://devnation-solutions.com/',
    "price": 4.99,
    "currency": 'EUR',
    'depends': [
        'dns_amount_to_text_dz',
        'l10n_dz_information_fiscale',
        'web',
    ],
    'data': [
        'views/res_company.xml',
        'views/res_partner.xml',

        'reports/account_move_report.xml',
        'reports/sale_order_report.xml',
        'reports/header_footer_report.xml',

        'data/report_layout.xml',
    ],
    'images': ['images/main_screenshot.gif'],

    'installable': True,
    'auto_install': False,
    'application':False,
}