# -*- coding: utf-8 -*-
{
    'name': 'MAGIMED Interne',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Gestion tracabilite complete pour conformite ISO - MAGIMED',
    'description': """
MAGIMED Interne - Module de Tracabilite ISO
============================================

Ce module fournit une gestion complete de la tracabilite pour la conformite ISO:

Fonctionnalites principales:
----------------------------
* Gestion amelioree des lots et numeros de serie
* Saisie simplifiee des lots avec dates d'expiration
* Alertes d'expiration automatiques
* Bons d'Entree Stock (Production, Manuels)
* Bons de Sortie Stock (Consommation, Rebuts)
* Bons de Transfert ameliores avec lots
* Historique detaille des mouvements avec filtrage avance
* Gestion des cautions sur factures clients
* Tableau de bord centralise

Rapports:
---------
* Bon d'Entree Stock
* Bon de Sortie Stock
* Bon de Transfert (avec lots et expirations)
* Liste des Lots
* Alertes d'Expiration
* Historique des Mouvements
    """,
    'author': 'ADI Development',
    'website': 'https://www.adidev.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'stock',
        'sale_stock',
        'product',
        'product_expiry',
        'account',
        'mail',
    ],
    'data': [
        # Security
        'security/magimed_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/ir_sequence_data.xml',
        'data/stock_picking_type_data.xml',
        'data/mail_template_data.xml',
        # Views
        'views/product_template_views.xml',
        'views/stock_production_lot_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_move_history_views.xml',
        'views/account_move_views.xml',
        'views/expiration_alert_views.xml',
        'views/dashboard_views.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        # Wizards
        'wizards/lot_quick_create_wizard_views.xml',
        'wizards/stock_move_history_wizard_views.xml',
        'wizards/expiration_report_wizard_views.xml',
        'wizards/confirm_expiry_magimed_view.xml',
        # Menus (must be after all actions are defined)
        'views/menus.xml',
        # Reports
        'report/report_paperformat.xml',
        'report/bon_entree_report.xml',
        'report/bon_sortie_report.xml',
        'report/bon_transfert_report.xml',
        'report/lot_list_report.xml',
        'report/expiration_alert_report.xml',
        'report/stock_history_report.xml',
        'report/iso_bl_valorise_report.xml',
        'report/iso_bl_non_valorise_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adi_magimed/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
