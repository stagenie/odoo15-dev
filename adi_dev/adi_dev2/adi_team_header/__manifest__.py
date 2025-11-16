{
    'name': 'Adicops Entete Personalisée ',
    'version': '17.0.1.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Adicops Entete Personalisée ',
    'description': "Adicops Entete Personalisée",
    "author": "ADICOPS",
    "email": 'info@adicops.com',

    "website": 'https://adicops.com/',
    'license': "AGPL-3",
    'depends': [
        'base',
        'contacts',
        'l10n_dz_information_fiscale'

    ],
    "data": [
        'security/ir.model.access.csv',
       'views/sales_team_view.xml',
        'views/report_templates.xml',

    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
