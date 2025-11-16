{
    'name': 'Adicops Product Sale History ',
    'version': '15.0.1.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Adicops Product Sale History ',
    'description': "Adicops Product Sale History",
    "author": "ADICOPS",
    "email": 'info@adicops.com',

    "website": 'https://adicops.com/',
    'license': "AGPL-3",
    'depends': [
        'base',
        'contacts',
        'sale_management' ,

    ],
   'data': [
        'security/ir.model.access.csv',
        'views/sale_order_line_views.xml',
        'wizard/product_sale_history_wizard.xml',

    ],
    
    
    #'assets': {
    #'web.assets_backend': [
     #       '/adi_sale_product_history/static/src/js/sale_history_button.js',
      #  ]
    
    
    'demo': [],
    'test': [],
    'qweb': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
