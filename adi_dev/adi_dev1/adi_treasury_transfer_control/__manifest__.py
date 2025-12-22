# -*- coding: utf-8 -*-
{
    'name': 'Treasury Transfer Control',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Contrôle avancé des transferts de trésorerie',
    'description': """
Treasury Transfer Control - Contrôle des Transferts de Trésorerie
==================================================================

Ce module ajoute des contrôles avancés sur les transferts de fonds entre :
- Caisses
- Coffres
- Banques

Fonctionnalités :
-----------------
* Vérification du solde disponible avant tout transfert (toutes sources)
* Vérification du montant maximum en destination
* Option pour autoriser/interdire les soldes négatifs par entité
* Contrôle du découvert autorisé pour les banques
* Messages d'alerte détaillés
* Historique des contrôles effectués
* Configuration flexible par type de transfert
    """,
    'author': 'ADI',
    'website': 'https://www.adi.com',
    'depends': [
        'adi_treasury',
        'adi_treasury_bank',
    ],
    'data': [
        # Sécurité - XML d'abord (définit les groupes), puis CSV
        'security/transfer_control_security.xml',
        'security/ir.model.access.csv',
        # Données
        'data/transfer_control_data.xml',
        # Vues
        'views/treasury_transfer_views.xml',
        'views/treasury_cash_views.xml',
        'views/treasury_safe_views.xml',
        'views/treasury_bank_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
