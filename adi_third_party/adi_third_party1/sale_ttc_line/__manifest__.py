##############################################################################
{
    'name': 'Montant TTC Ligne de Devis',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Ajoute le montant TTC dans les lignes de devis',
    'description': """
        Ce module ajoute un champ calculé pour afficher le montant TTC 
        (HT + TVA 19%) dans les lignes de commande/devis.
    """,
    'author': 'Votre Entreprise',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

##############################################################################