# -*- coding: utf-8 -*-
{
    'name': 'Exclusion de Factures des Rapports Comptables',
    'version': '15.0.2.0.0',
    'category': 'Accounting/Reports',
    'summary': 'Exclure des factures du calcul des soldes dans tous les rapports comptables',
    'description': """
        Module d'Exclusion de Factures des Rapports Comptables
        =======================================================

        Ce module permet d'exclure des factures spécifiques du calcul des soldes
        dans tous les rapports et vues comptables d'Odoo.

        Fonctionnalités :
        -----------------
        * Ajout d'un champ booléen sur les factures pour les marquer comme exclues
        * Exclusion automatique dans le Partner Ledger (Livre des tiers)
        * Exclusion automatique dans le General Ledger (Grand livre)
        * Exclusion dans les vues comptables natives d'Odoo
        * Filtres pour masquer/afficher les écritures exclues
        * Menu dédié pour visualiser les factures exclues
        * Compatible avec le module accounting_pdf_reports (Odoo Mates)

        Rapports et vues affectés :
        ---------------------------
        * Partner Ledger (Livre des tiers) - PDF et vue liste
        * General Ledger (Grand livre) - PDF et vue liste
        * Vue des écritures comptables
        * Tous les calculs de soldes dans les vues comptables

        Utilisation :
        -------------
        1. Ouvrir une facture client ou fournisseur
        2. Cocher "Ne pas inclure dans le calcul du Solde"
        3. Les rapports et vues n'incluront plus cette facture dans les soldes
        4. Utiliser les filtres dans les vues pour masquer/afficher les exclusions
        5. Menu "Factures exclues" pour voir toutes les factures marquées

        Note :
        ------
        Ce module étend les rapports du module accounting_pdf_reports
        et les vues comptables natives d'Odoo 15.
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'accounting_pdf_reports',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/account_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
