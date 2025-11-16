{
    'name': 'ADICOPS Invoiced Quantity',
    'version': '15.0.0.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Invoiced Quantity . ',
    'description': "Invoiced Quantity. ",
    "author" : "ADICOPS",
    "email": 'info@adicops.com',
    "website":'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'account',        
        'base',           
        'product',        
        'stock',
        #
        #  'website'
    ], 
    "data":  [
       # 'security/ir.model.access.csv',
        'views/views.xml',
        ],
    'post_init_hook': 'force_recompute_qte_fields', 
    'demo': [],
    'test': [],
    'qweb': [],    
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
