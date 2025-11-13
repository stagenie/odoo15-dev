# -*- coding: utf-8 -*-
{
    'name': 'Enregistrement Automatique',
    'version': '15.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Enregistrement automatique pour Devis/Commandes et Achats',
    'description': """
        Module d'enregistrement automatique :
        - Sauvegarde automatique des Devis/Bons de commandes
        - Sauvegarde automatique des Demandes d'achat/Commandes d'achat
        - Configuration de l'intervalle d'enregistrement
        - Notification visuelle lors de la sauvegarde
    """,
    "author": "ADICOPS",
    "email": 'info@adicops.com',
    "website": 'https://adicops.com/',
    'depends': ['sale_management', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adi_auto_save/static/src/js/auto_save.js',
            'adi_auto_save/static/src/css/auto_save.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
