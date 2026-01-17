# -*- coding: utf-8 -*-
{
    'name': 'Ajout de lignes depuis factures',
    'version': '15.0.2.0.0',
    'category': 'Accounting/Invoicing',
    'summary': 'Ajouter des lignes de facture depuis d\'autres factures validées',
    'description': """
        Ce module permet d'ajouter des lignes de facture depuis d'autres factures validées.

        Fonctionnalités:
        * Bouton "Ajouter depuis Factures" sur les factures brouillon
        * Wizard simple pour sélectionner les factures sources
        * Copie des lignes avec traçabilité
        * Même partenaire obligatoire
        * Seules les factures validées peuvent être sources

        Cas d'usage:
        * Regrouper plusieurs factures en une seule
        * Dupliquer des lignes entre factures liées
        * Consolider des factures pour un même client
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_line_sync_wizard_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
