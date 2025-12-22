# -*- coding: utf-8 -*-
{
    'name': 'Type de Rapport par Journal',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Invoicing',
    'summary': 'Sélection du type de rapport d\'impression selon le journal de facturation',
    'description': """
Ce module permet de configurer le type de rapport d'impression par journal de facturation.

Fonctionnalités:
* Champ "Type de rapport" sur les journaux de vente
* Boutons d'impression conditionnels sur les factures
* Affiche "AB Facture" si type = Facture
* Affiche "Vente" / "Vente TTC" si type = Vente
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'l10n_dz_droit_timbre',
        'l10n_dz_information_fiscale',
        'adi_ab_invoice_reports',
        'mai_customer_overdue_balance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_print_warning_wizard_views.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'views/report_invoice_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
