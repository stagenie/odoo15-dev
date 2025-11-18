# -*- coding: utf-8 -*-
{
    'name': 'Exclusion de Factures du Partner Ledger',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Reports',
    'summary': 'Permet d\'exclure des factures spécifiques du calcul du solde dans le Partner Ledger',
    'description': """
        Module d'Exclusion de Factures du Partner Ledger
        ==================================================

        Ce module étend le rapport Partner Ledger pour permettre l'exclusion
        de certaines factures spécifiques du calcul des soldes clients/fournisseurs.

        Fonctionnalités :
        -----------------
        * Ajout d'un champ booléen sur les factures pour les marquer comme exclues
        * Exclusion automatique de ces factures dans le calcul du Partner Ledger
        * Compatible avec le module accounting_pdf_reports (Odoo Mates)
        * Interface simple pour gérer les exclusions

        Utilisation :
        -------------
        1. Ouvrir une facture client ou fournisseur
        2. Cocher la case "Exclure du Partner Ledger" si nécessaire
        3. Les rapports Partner Ledger n'incluront pas cette facture dans les soldes

        Note :
        ------
        Ce module étend le rapport Partner Ledger du module accounting_pdf_reports.
        Il est compatible avec le module tis_partner_ledger_filter_balance.
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
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
