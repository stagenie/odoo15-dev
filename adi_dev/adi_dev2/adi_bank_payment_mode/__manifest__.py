{
    'name': 'Bank Payment Extension',
    'version': '15.0.1.0.0',
     'sequence': 1,
    'category': 'Accounting/Accounting',
    'summary': 'Extend payment modes for bank journals',
    'depends': ['account'],
    'description': "Adicops Entete Personalisée",
    "author": "ADICOPS",
    "email": 'info@adicops.com',

    "website": 'https://adicops.com/',
    'license': "AGPL-3",
    'data': [
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}