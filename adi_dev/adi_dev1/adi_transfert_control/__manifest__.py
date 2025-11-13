# -*- coding: utf-8 -*-
{
    'name': 'Contrôle des Transferts',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Contrôle des transferts entre caisses et banques avec affichage des soldes',
    'description': """
        Ce module permet de contrôler les transferts entre comptes.
        - Empêche les transferts si le solde du compte source est insuffisant
        - Affiche les soldes des journaux source et destination
        - Alerte visuelle en rouge si le montant dépasse le solde
    """,
    'author': 'ADICOPS',
    'website': 'adicops-dz.com',
    'email': 'info@adicops.com',
    'depends': ['account'],
    'data': [
        'views/account_payment_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adi_transfert_control/static/src/css/payment_form.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}