{
    'name': 'Customer Overdue Balance',
    'version' : '15.1.1.1',
    'category': 'Invoicing',
    'sequence': 1,
    'summary': 'Customer Overdue Balance',
    'description': 
     """ 
        Using this module you can calculate customer overdue balance in the customer invoice.
     """,
    "author" : "MAISOLUTIONSLLC",
    "email": 'apps@maisolutionsllc.com',
    "website":'http://maisolutionsllc.com/',
    'license': 'OPL-1',
    'currency': 'EUR',    
    'price': 7,
    'depends': ["l10n_dz_droit_timbre",
        "account"],
    'data': [
        'views/views.xml',
        'views/res_partner_view.xml',
    ],
    'demo': [],
    "live_test_url" : "https://youtu.be/RcxjbywqUmA",
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}


