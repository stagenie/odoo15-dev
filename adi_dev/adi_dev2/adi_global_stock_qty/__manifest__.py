# -*- coding: utf-8 -*-
{
    'name': 'Quantité Globale Stock - Bypass Restrictions',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Affiche la quantité totale en stock pour tous les utilisateurs sans révéler les emplacements',
    'description': """
Quantité Globale Stock - Bypass Restrictions
=============================================

Ce module permet aux utilisateurs des applications Vente, Inventaire et Achat
de consulter la quantité TOTALE disponible d'un article, même s'ils ont des
restrictions sur certains emplacements de stock.

Fonctionnalités:
----------------
* Affichage de la quantité totale disponible (tous emplacements confondus)
* Bypass des restrictions d'emplacement en lecture seule
* Aucune information sur les emplacements individuels n'est révélée
* Accessible aux utilisateurs Vente/Inventaire/Achat

Sécurité:
---------
* Lecture seule uniquement
* Les emplacements restent masqués pour les utilisateurs non autorisés
* Utilise sudo() uniquement pour l'agrégation des quantités
    """,
    'author': 'ADI Dev',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'sale',
        'purchase',
        'devnix_available_qty',
    ],
    'data': [
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
