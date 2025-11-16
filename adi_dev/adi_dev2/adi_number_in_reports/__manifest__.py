{
    'name': 'ADICOPS Number in reports',
    'version': '15.0.0.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'ADICOPS Number in reports . ',
    'description': "ADICOPS Number in reports . ",
    "author" : "ADICOPS",
    "email": 'info@adicops.com',
    "website":'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        'product',
        'account',
        'purchase',
        'stock',
        #
        #  'website'
    ], 
    "data":  [
       # 'security/ir.model.access.csv',
        'views/report_views.xml',
       # 'views/form_views.xml',
        ],
    'demo': [],
    'test': [],
    'qweb': [],    
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
