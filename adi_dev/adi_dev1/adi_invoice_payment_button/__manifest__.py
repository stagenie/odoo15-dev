# -*- coding: utf-8 -*-
{
    'name': 'Smart Button Paiements sur Factures',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Invoicing',
    'summary': 'Ajoute un Smart Button pour afficher les paiements liés à une facture',
    'description': """
Ce module ajoute un Smart Button sur les factures (clients et fournisseurs)
permettant de visualiser rapidement les paiements associés.

Fonctionnalités:
* Affichage du nombre de paiements liés à la facture
* Accès direct à la liste des paiements en cliquant sur le bouton
* Fonctionne pour les factures clients et fournisseurs
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
