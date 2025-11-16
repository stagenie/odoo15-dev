# -*- coding: utf-8 -*-
{
    'name': "Mobile Point Of Sale (Android/IPhone)",

    'summary': """
      Experience seamless mobile point of sale (POS) management with the Odoo Mobile Point of Sale  app""",

    'description': """
        This is only the Backend that you need to activate the mobile app , 
        Experience seamless mobile point of sale (POS) management with the Odoo Mobile Point of Sale Backend app. Our
        powerful backend solution enhances your mobile POS experience by providing a comprehensive suite of features for
        effortless payment processing and streamlined customer relationship management (CRM).
    """,

    'author': "Odoo Station",
        'website': "https://t.me/odoo_station/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

'images':['static\src\image\iodoo_icon.png'],
    'price': 0,
    'currency': 'EUR',
    'images': ['images/main_screenshot.png','images/main_screenshot.png'    ],
}
