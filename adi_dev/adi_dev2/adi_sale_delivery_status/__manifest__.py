{
    'name': 'Suivi Statut de Livraison',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Ajoute un statut de livraison sur les commandes de vente',
    'description': """
        Ajoute un champ "Statut de Livraison" (Livré, Non Livré, Partiellement Livré)
        sur les commandes de vente avec possibilité de filtrage et regroupement.
    """,
    'depends': ['sale_stock'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
