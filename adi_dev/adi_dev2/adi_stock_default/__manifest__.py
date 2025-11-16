{
    'name': 'ADICOPS Stockable by default',
    'version': '15.0.0.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Ce Module permet la RAZ Price Lists des prix de vente des produits épuisés  . ',
    'description': "Ce Module permet la RAZ Price Lists des prix de vente des produits épuisés  . ",
    "author" : "ADICOPS",
    "email": 'info@adicops.com',
    "website":'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'product',
        'account',
        'purchase',
        'stock',
        #
        #  'website'
    ], 
    "data":  [
       # 'security/ir.model.access.csv',
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
