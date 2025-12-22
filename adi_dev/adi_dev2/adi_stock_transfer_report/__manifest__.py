{
    'name': 'ADI Stock Transfer Report',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Bon de Transfert légal avec en-têtes équipes commerciales',
    'description': """
        Module de rapport pour les transferts de stock inter-entrepôts.

        Fonctionnalités:
        - Lien entre entrepôts et équipes commerciales
        - Responsable de réception sur les transferts
        - Rapport "Bon de Transfert" légal avec:
            * En-tête: informations équipe source
            * Destinataire: informations équipe destination (comme un client)
            * Informations fiscales (RC, NIF, AI, NIS)
            * Liste des articles avec quantités formatées
    """,
    'author': 'ADI',
    'website': '',
    'depends': [
        'adi_stock_transfer',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/stock_transfer_paperformat.xml',
        'report/stock_transfer_report.xml',
        'report/stock_transfer_template.xml',
        'views/stock_warehouse_views.xml',
        'views/stock_transfer_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
