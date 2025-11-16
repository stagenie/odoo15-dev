{
    'name': 'ADI Total Amount due',
    'version': '15.0.0.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'ADI Total Amount due . ',
    'description': "ADI Total Amount due  . ",
    "author" : "ADICOPS",
    "email": 'info@adicops.com',
    "website":'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',

        #
        #  'website'
    ], 
    "data":  [
       'views/account_move_view.xml',
       # 'views/product.xml',
        ],
    'demo': [],
    'test': [],
    'qweb': [],    
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
