# -*- coding: utf-8 -*-
{
    'name': 'Gestion des Retours Fournisseurs',
    'version': '15.0.1.0.0',
    'category': 'Purchase',
    'sequence': 16,
    'summary': 'Gestion des retours fournisseurs avec creation automatique d\'avoirs',
    'description': """
        Module de Gestion des Retours Fournisseurs
        ==========================================

        Fonctionnalites :
        - Gestion des ordres de retour fournisseur avec workflow (Brouillon -> Valide -> Avoir cree)
        - Configuration des raisons de retour
        - Plusieurs options d'origine flexibles :
          * Origine stricte : commandes achat et BR specifiques
          * Origine souple : tout produit deja recu du fournisseur
          * Sans origine : choix libre des produits
        - Selection de l'entrepot et de l'emplacement source
        - Creation automatique des avoirs fournisseurs
        - Creation automatique des expeditions de retour
        - Rapport PDF bon de retour
        - Menu Analyse avec vues Pivot et Graphiques
        - Tracabilite complete via chatter
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'purchase_stock',
        'account',
        'stock',
        'adi_return_management',
    ],
    'data': [
        # Securite (doit etre en premier)
        'security/supplier_return_security.xml',
        'security/ir.model.access.csv',
        # Donnees
        'data/supplier_return_data.xml',
        # Rapport
        'report/supplier_return_order_report.xml',
        # Wizard
        'wizard/supplier_return_order_add_products_wizard_views.xml',
        # Vues
        'views/supplier_return_reason_views.xml',
        'views/supplier_return_order_views.xml',
        'views/supplier_return_analysis_views.xml',
        'views/res_config_settings_views.xml',
        'views/supplier_return_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
