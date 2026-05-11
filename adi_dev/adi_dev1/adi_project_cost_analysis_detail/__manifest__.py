{
    'name': 'Analyse des Coûts Projets — Détail Factures',
    'category': 'Project',
    'version': '15.0.1.0',
    'summary': 'Détaille les dépenses projet par facture fournisseur',
    'author': 'ADICOPS',
    'email': 'info@adicops.com',
    'website': 'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'adi_project_cost_analysis',
    ],
    'data': [
        'report/project_cost_analysis_detail_report.xml',
        'views/wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
