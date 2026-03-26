{
    'name': 'Sale Report - Repeat Table Header',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Repeat table header on each page in sale order PDF reports',
    'depends': ['sale', 'l10n_dz_reports'],
    'data': [
        'views/sale_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
