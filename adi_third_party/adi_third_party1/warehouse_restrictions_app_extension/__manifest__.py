{
    'name': 'Warehouse Restrictions App Extension',
    'version': '15.0.1.0.0',
    'author': 'Votre Société',
    'category': 'Inventory',
    'depends': [
        'warehouse_restrictions_app',  
        'stock'
    ],
    'data': [
        'security/warehouse_restrictions_app_extension_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}