# __manifest__.py
{
    'name': 'Stock Quantities by Warehouse',
    'version': '15.0.1.0.0',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}