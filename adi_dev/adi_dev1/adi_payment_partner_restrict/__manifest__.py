# -*- coding: utf-8 -*-
{
    'name': 'Restriction Création Partenaires - Paiements & Trésorerie',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': """Désactive la création de partenaires depuis les paiements et opérations de trésorerie""",
    'description': """
        Ce module désactive les options de création rapide (Créer et Créer et modifier)
        pour les partenaires dans les contextes suivants :

        - Paiements clients et fournisseurs
        - Opérations de caisse
        - Opérations bancaires
        - Opérations de coffre

        Cela évite de polluer la base des contacts avec des entrées incomplètes ou en double
        créées à la volée depuis ces formulaires.

        Les utilisateurs doivent sélectionner uniquement des partenaires existants.
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'support': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'adi_treasury',
        'adi_treasury_bank',
    ],
    'data': [
        'views/account_payment_views.xml',
        'views/treasury_cash_operation_views.xml',
        'views/treasury_bank_operation_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
