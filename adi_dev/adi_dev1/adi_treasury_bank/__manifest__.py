# -*- coding: utf-8 -*-
{
    'name': 'Gestion de Trésorerie Bancaire',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Gestion des comptes bancaires et opérations bancaires',
    'description': """
Gestion de Trésorerie Bancaire
================================

Ce module étend la gestion de trésorerie pour gérer les comptes bancaires.

Fonctionnalités principales :
------------------------------
* Gestion des comptes bancaires liés aux journaux de type 'bank'
* Opérations bancaires avec dates de valeur
* Méthodes de paiement bancaires (virement, chèque, carte, prélèvement)
* Rapprochement bancaire et gestion des relevés
* Gestion du découvert autorisé
* Transferts étendus : banque↔caisse, banque↔coffre, banque↔banque
* Regroupement des opérations par type
* Rapports de clôture bancaire et relevés de compte
* Intégration automatique avec les paiements Odoo

Différences avec la caisse :
----------------------------
* Pas de comptage physique de billets/pièces
* Clôture périodique (non quotidienne obligatoire)
* Date d'opération vs date de valeur
* Découvert autorisé avec limite
* Références bancaires (numéros de chèque, références virement)
* Rapprochement bancaire au lieu de simple comptage

    """,
    'author': 'ADICOPS',
    'website': 'https://www.adicops.com',
    'depends': [
        'base',
        'account',
        'adi_treasury',  # Dépend du module de trésorerie de base
    ],
    'data': [
        # Sécurité
        'security/treasury_bank_security.xml',
        'security/ir.model.access.csv',

        # Données
        'data/treasury_bank_data.xml',

        # Vues
        'views/treasury_bank_views.xml',
        'views/treasury_bank_operation_views.xml',
        'views/treasury_bank_closing_views.xml',
        'views/treasury_transfer_views.xml',
        'views/treasury_bank_menu.xml',

        # Rapports
        'reports/treasury_bank_closing_report.xml',
        'reports/treasury_bank_statement_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
