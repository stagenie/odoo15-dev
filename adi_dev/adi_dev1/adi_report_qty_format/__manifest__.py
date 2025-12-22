# -*- coding: utf-8 -*-
{
    'name': 'Format Quantités Rapports',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Invoicing',
    'summary': 'Supprime les décimales inutiles dans les quantités des rapports',
    'description': """
Ce module formate les quantités dans les rapports (factures, devis, proformas, BL)
pour ne pas afficher les décimales inutiles.

Exemples:
* 5.00 → 5
* 5.50 → 5.5
* 5.123 → 5.123
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'license': 'LGPL-3',
    'depends': [
        'l10n_dz_droit_timbre',
        'adi_ab_invoice_reports',
        'adi_ab_sale_reports',
    ],
    'data': [
        'views/report_qty_format.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
