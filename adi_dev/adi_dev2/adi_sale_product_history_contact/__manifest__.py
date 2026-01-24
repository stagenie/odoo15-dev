# -*- coding: utf-8 -*-
{
    'name': 'Adicops Sale Product History - Contact Filter',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Ajoute un filtre par contact dans l\'historique des prix de vente',
    'description': """
Adicops Sale Product History - Contact Filter
==============================================

Ce module ajoute un filtre par contact (client) dans le wizard d'historique
des prix de vente.

Fonctionnalités:
- Filtre par contact dans l'historique des ventes
- Par défaut, le contact du devis/commande en cours est sélectionné
- Possibilité de consulter les ventes/devis d'autres clients pour le même produit
    """,
    'author': 'Adicops',
    'website': 'https://www.adicops.com',
    'depends': [
        'adi_sale_product_history',
    ],
    'data': [
        'wizard/product_sale_history_contact_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
