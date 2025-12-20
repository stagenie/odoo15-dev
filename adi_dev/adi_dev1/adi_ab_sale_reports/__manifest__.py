# -*- coding: utf-8 -*-
{
    'name': 'AB Sale Reports - Rapports Ventes Personnalisés',
    'version': '15.0.1.0.0',
    'summary': 'Personnalisation des rapports de vente pour AB',
    'description': """
        Personnalisation des rapports de vente:

        1. Rapport Devis:
           - Sans échéance
           - Affichage TTC dans les lignes
           - Sans colonne TVA ni remise
           - Net à payer en bas
           - Offre valable jusqu'à...

        2. Rapport Proforma:
           - Sans échéance
           - Tout standard (HT, TVA, remise)
           - Net à payer en bas (remplace Total TTC)
           - Offre valable jusqu'à...

        3. Rapport Bon de Commande:
           - Sans colonne TVA
           - Remise avec 2 décimales
           - Total TTC dans les lignes
           - Net à payer en bas
           - Délai de livraison
           - Modalités de paiement configurables
    """,
    'category': 'Sales',
    'author': 'ADI',
    'website': '',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/payment_modality_data.xml',
        'views/payment_modality_views.xml',
        'views/sale_order_views.xml',
        'report/ab_quotation_report.xml',
        'report/ab_proforma_report.xml',
        'report/ab_saleorder_report.xml',
        'report/ab_stock_picking_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
