# -*- coding: utf-8 -*-
{
    'name': 'ADI OPP Number',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Ajoute le champ OPP Number sur les devis/commandes',
    'description': """
        Ce module ajoute un champ OPP Number sur les devis et commandes de vente.
        Le champ est également affiché dans les rapports (Devis, Proforma, Commande).
    """,
    'author': 'ADI',
    'website': '',
    'depends': ['sale', 'sale_management'],
    'data': [
        'views/sale_order_views.xml',
        'reports/sale_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
