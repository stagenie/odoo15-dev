{
    'name': 'Total Discount',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Calculate and display total discount amount',
    'description': """
    This module adds the total discount amount to sale orders,
    displaying it below the untaxed amount in both form view and printed report.
    """,
    "author" : "ADICOPS",
    "email": 'info@adicops.com',
    "website":'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': ['sale','account'],
    'data': [
        'views/views.xml',
        'reports/sale_order_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}