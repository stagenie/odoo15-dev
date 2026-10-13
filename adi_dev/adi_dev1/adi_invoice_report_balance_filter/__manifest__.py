{
    'name': 'Adi Invoice Report Balance Filter',
    'version': '15.0.1.0.0',
    'sequence': 1,
    'category': 'Accounting',
    'summary': "Ajoute le filtre 'Solde inclus' (par défaut) dans l'Analyse de Facture.",
    'description': "ADI - Filtre 'Solde inclus' / 'Hors solde' sur l'Analyse de Facture "
                   "(account.invoice.report), aligné sur le comportement des Factures Clients.",
    "author": "ADICOPS",
    "email": 'info@adicops.com',
    "website": 'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'adi_partner_ledger_exclude',  # fournit le champ exclude_from_partner_ledger
    ],
    "data": [
        'views/account_invoice_report_views.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
