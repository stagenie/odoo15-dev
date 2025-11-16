{
    'name': 'ADI Stock Transfer Management',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Gestion avancée des transferts inter-dépôts avec validation à deux niveaux',
    'description': """
        Module de gestion des transferts de stock entre dépôts
        ========================================================
        
        Fonctionnalités principales:
        - Transferts inter-dépôts avec validation à deux niveaux
        - Contrôle des quantités disponibles en temps réel
        - Gestion multi-sociétés et multi-entrepôts
        - Accès spécifiques pour demandeurs et validateurs
        - Traçabilité complète des transferts
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'depends': ['base', 'stock', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/stock_transfer_views.xml',
        'views/stock_transfer_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
