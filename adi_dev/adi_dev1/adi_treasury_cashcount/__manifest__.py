# -*- coding: utf-8 -*-
{
    'name': 'Comptage des Billets et Pièces',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Comptage détaillé des billets et pièces lors de la clôture de caisse',
    'description': """Module de Comptage des Billets et Pièces

Extension du module adi_treasury pour permettre :
- Comptage détaillé des billets et pièces par dénomination
- Calcul automatique du solde réel à partir du comptage
- Gestion des dénominations (2000 DA, 1000 DA, 500 DA, etc.)
- Interface intuitive de saisie du comptage

Lors de la clôture de caisse, l'utilisateur peut saisir :
- Nombre de billets de 2000 DA
- Nombre de billets de 1000 DA
- Nombre de billets de 500 DA
- Nombre de pièces de 200 DA, 100 DA, 50 DA, etc.

Le montant total est calculé automatiquement et mis à jour dans le solde réel.
""",
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': ['adi_treasury'],
    'data': [
        'security/ir.model.access.csv',
        'data/cash_denominations.xml',
        'views/cash_denomination_views.xml',
        'views/treasury_cash_closing_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
