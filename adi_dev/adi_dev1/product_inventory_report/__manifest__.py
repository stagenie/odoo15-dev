# -*- coding: utf-8 -*-
{
    'name': 'Rapport Inventaire Produits par Emplacement',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Rapport d\'inventaire détaillé avec quantités par emplacement',
    'description': """
        Rapport d'Inventaire Produits par Emplacement
        ===============================================

        Fonctionnalités :
        - Affichage de la liste des produits avec quantités par emplacement
        - Filtrage par catégorie de produit
        - Option pour afficher uniquement les produits en stock
        - Support multi-emplacements et multi-entrepôts
        - Export et impression du rapport
        - Vue dynamique avec colonnes par emplacement
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'license': 'LGPL-3',
    'depends': ['stock', 'product'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/product_inventory_report_wizard_views.xml',
        'views/product_inventory_report_views.xml',
        'reports/product_inventory_report_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
