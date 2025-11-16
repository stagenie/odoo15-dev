{
    'name': 'Bons de Livraison Globaux',
    'version': '15.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Regroupement des bons de livraison',
    'depends': ['stock', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/global_delivery_views.xml',
        'wizard/create_global_delivery_views.xml',
    ],
    'sequence' : '1',
    'installable': True,
    'application': True,
}