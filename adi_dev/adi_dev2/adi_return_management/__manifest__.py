# -*- coding: utf-8 -*-
{
    'name': 'Gestion des Retours',
    'version': '15.0.3.0.0',
    'category': 'Sales',
    'sequence': 15,
    'summary': 'Gestion des retours clients avec creation automatique d\'avoirs',
    'description': """
        Module de Gestion des Retours Clients
        ======================================

        Fonctionnalites :
        - Gestion des ordres de retour avec workflow (Brouillon -> Valide -> Avoir cree)
        - Configuration des raisons de retour
        - Plusieurs options d'origine flexibles :
          * Origine stricte : commandes et BL specifiques
          * Origine souple : tout produit deja livre au client
          * Sans origine : choix libre des produits
        - Selection de l'entrepot puis de l'emplacement de retour
        - Filtrage des entrepots par equipe commerciale
        - Creation automatique des avoirs clients
        - Tracabilite complete via chatter
        - Prix de vente original depuis la commande client
        - Menu Analyse avec vues Pivot et Graphiques :
          * Tableau croise dynamique (TCD)
          * Evolution des retours dans le temps
          * Repartition par raison (camembert)
          * Top clients / entrepots
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_stock',
        'account',
        'stock',
        'sales_team',
        'warehouse_restrictions_app',
        'adi_stock_transfer_report',
    ],
    'data': [
        # Securite (doit etre en premier)
        'security/return_security.xml',
        'security/ir.model.access.csv',
        # Donnees
        'data/return_data.xml',
        # Rapport
        'report/return_order_report.xml',
        # Wizard
        'wizard/return_order_add_products_wizard_views.xml',
        # Vues
        'views/return_reason_views.xml',
        'views/return_order_views.xml',
        'views/return_order_analysis_views.xml',
        'views/res_config_settings_views.xml',
        'views/return_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
