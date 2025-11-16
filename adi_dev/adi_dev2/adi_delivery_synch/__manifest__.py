{
    'name': 'AdI Delivery Status  ',
    'version': '15.1.1.1',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'AdI Delivery Status   ',
    'description': "AdI Delivery Status  ,...  ",
    "author" : "ADICOPS",
    "email": 'info@adicops.com',
    
    "website":'https://adicops.com/',
    'license': "AGPL-3", 
    'depends': [
        'base',
        'product',        
        'sale',
        'stock',
    ], 
    "data":  [                
          
       'views/sale_order_view.xml',
        'reports/sale_order_report.xml',

         
    
        ],
    'demo': [],
    'test': [],
    'qweb': [],    
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
