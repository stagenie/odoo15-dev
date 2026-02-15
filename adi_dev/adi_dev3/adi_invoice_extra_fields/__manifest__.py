{
    'name': 'FActure Extra fields',
    'version': '15.0.1.0.0',
    'category': 'Inventory',
    'summary': 'FActure Extra fields',
    'depends': ['stock', 'base','account'],
    'data': [
        #'security/ir.model.access.csv',
        'views/account_move_views.xml',
        #'reports/report_invoice_document.xml',
    ],
    'sequence' : '1',
    'installable': True,
    'application': True,
}