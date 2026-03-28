# -*- coding: utf-8 -*-
{
    'name': 'Correctif Qté Disponible Achat - Par Entrepôt',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': "Corrige la quantité disponible sur les lignes d'achat pour afficher le stock de l'entrepôt sélectionné",
    'description': """
Correctif Qté Disponible Achat
===============================

Corrige le calcul du champ "Qté Disponible" sur les lignes de commande d'achat
pour afficher la quantité disponible dans l'entrepôt sélectionné (Recevoir dans)
au lieu de la quantité globale tous entrepôts confondus.
    """,
    'author': 'ADI Dev',
    'license': 'LGPL-3',
    'depends': [
        'purchase_stock',
        'devnix_available_qty',
    ],
    'installable': True,
    'auto_install': True,
}
