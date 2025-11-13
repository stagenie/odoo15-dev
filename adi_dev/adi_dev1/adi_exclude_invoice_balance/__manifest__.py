# -*- coding: utf-8 -*-
{
    'name': 'Exclusion Factures du Solde Partenaire',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Exclure certaines factures/avoirs du calcul des soldes clients/fournisseurs',
    'description': """
        Module d'exclusion de factures du solde partenaire :
        - Permet de marquer une facture/avoir comme exclus du calcul des soldes
        - Affecte les rapports Partner Ledger
        - Affecte les vues comptables (crédit, débit, solde)
        - Par défaut, toutes les factures sont incluses dans les calculs
        - Compatible avec les modules de comptabilité tiers
    """,
    "author": "ADICOPS",
    "email": 'info@adicops.com',
    "website": 'https://adicops.com/',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
