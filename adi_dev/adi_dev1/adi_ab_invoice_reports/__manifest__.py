# -*- coding: utf-8 -*-
{
    'name': 'AB Invoice Reports - Rapports Factures Personnalisés',
    'version': '15.0.1.3.0',
    'summary': 'Personnalisation des rapports de factures pour AB',
    'description': """
        Personnalisation des rapports de factures (par héritage):

        1. AB Facture (hérite de ADI Facture):
           - Sans Date échéance et Origine
           - Remise avec 2 décimales
           - Mode de règlement en bas

        2. Vente (hérite de ADI BL):
           - Sans titre "Bon de livraison"
           - Sans Origine et Date échéance
           - Remise avec 2 décimales

        3. Vente TTC:
           - Sans titre "Bon de livraison"
           - Sans Date échéance et Origine
           - Total TTC dans les lignes
           - Sans colonne TVA
           - Net à payer seulement en bas
    """,
    'category': 'Accounting',
    'author': 'ADI',
    'website': '',
    'depends': [
        'base',
        'account',
        'sale',
        'l10n_dz_droit_timbre',
        'adi_bank_payment_mode',
        'adi_invoice_payment_button',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/payment_display_config_views.xml',
        'views/account_move_views.xml',
        'report/ab_invoice_inherit.xml',
        'report/ab_vente_inherit.xml',
        'report/ab_vente_ttc_report.xml',
        'report/tax_totals_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
