# -*- coding: utf-8 -*-
{
    'name': "Activit\u00e9 Client/Fournisseur",
    'category': 'Accounting/Accounting',
    'summary': "Ajouter l'activit\u00e9 du partenaire et contr\u00f4ler l'impression des factures",
    'version': '15.0.1.1',
    'author': 'ADI',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'l10n_dz_information_fiscale',
        'l10n_dz_droit_timbre',
        'adi_journal_report_type',
        'adi_ab_invoice_reports',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'wizard/invoice_print_warning_wizard_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'reports/report_invoice.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
