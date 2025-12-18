# -*- coding: utf-8 -*-
{
    'name': 'AB Energie - Rapports Personnalisés',
    'version': '15.0.1.0.0',
    'summary': 'Personnalisation des rapports pour AB Energie',
    'description': """
        Personnalisation des rapports de vente pour AB Energie:
        - Devis avec affichage TTC
        - Proforma personnalisé
        - Bon de commande avec délais et modalités de paiement
        - Bon de livraison
        - Factures personnalisées
        - Bon de livraison valorisé
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
        'sale_discount_total',  # Module pour les remises
        'adi_team_header',  # Module d'en-tête personnalisé
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        # 'views/report_template_inherit.xml',  # Désactivé - correction faite directement dans adi_team_header
        'report/report_paperformat.xml',
        # Nouveaux rapports personnalisés complets
        'report/ab_sale_reports.xml',  # Devis et Proforma
        'report/ab_order_reports.xml',  # Bon de commande
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
