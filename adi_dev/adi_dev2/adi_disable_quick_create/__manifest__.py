# -*- coding: utf-8 -*-
{
    'name': 'Désactiver Création Rapide Produits et Partenaires',
    'version': '1.0.0',
    'category': 'Technical',
    'summary': """Désactive les options 'Créer' et 'Créer et modifier' pour les produits et partenaires""",
    'description': """
        Ce module désactive les options de création rapide (quick create) pour :
        - Les produits dans tous les formulaires
        - Les clients et fournisseurs dans les modules vente, achat et comptabilité

        Cela force les utilisateurs à sélectionner uniquement des enregistrements existants.
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'support': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'purchase',
        'account',
        'stock',
    ],
    'data': [
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/account_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
