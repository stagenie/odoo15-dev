# -*- coding: utf-8 -*-

{
    'name': "Droit de Timbre (Timbre de quittances)",
    'category': 'Accounting/Accounting',
    'summary': """ Droit de Timbre (Timbre de quittances) - odoo 14 """,
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
    ],
    'data': [
        'views/droit_timbre.xml',
        'views/account_payment_mode.xml',
        'views/account_move.xml',

        'data/account_payment_mode_datas.xml',

      #'reports/account_move_report.xml',
      'reports/account_report.xml',
      'reports/report_invoice.xml',
       'reports/report_invoice_bl.xml',

        'security/ir.model.access.csv',
    ],
    'images': ['images/main_screenshot.gif'],

    'post_init_hook': "post_init_hook",

    'installable': True,
    'auto_install': False,
    'application': False,
}