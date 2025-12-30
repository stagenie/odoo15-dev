{
    'name': 'Adi Partner Credit Limit - Delivery Block',
    'version': '15.0.2.0.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Option de blocage limite crédit à la commande ou à la livraison',
    'description': """
        Extension du module de limite de crédit client.

        Fonctionnalités :
        - Choix du moment de blocage : à la commande ou à la livraison
        - Message d'avertissement non bloquant sur la commande (optionnel)
        - Wizard de configuration en masse des clients
        - Menu dans Ventes > Configuration
    """,
    'author': 'ADICOPS',
    'email': 'info@adicops.com',
    'website': 'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'adi_partner_credit_limit',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/partner_credit_limit_wizard_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
