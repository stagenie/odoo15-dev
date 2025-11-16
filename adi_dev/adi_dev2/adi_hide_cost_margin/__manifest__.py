{
    'name': 'ADICOPS Hide Cost and Marge',
    'version': '1.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Hide Cost and Marge. ',
    'description': "Hide Cost and Marge ",
    "author" : "ADICOPS",
    "email": 'info@adicops.com',
    "website":'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'base',        
        'product',
        'sale',
        'sale_margin'        

        #
        #  'website'
    ], 
    "data":  [
        'security/groups.xml',
        'views/views.xml',
        ],    
    'demo': [],
    'test': [],
    'qweb': [],    
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
