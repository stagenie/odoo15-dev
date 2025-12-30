# -*- coding: utf-8 -*-
{
    'name': 'ADI Stock Transfer Enhanced',
    'version': '15.0.2.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Réservation multi-emplacement et restriction par équipe pour les transferts',
    'description': """
ADI Stock Transfer Enhanced
===========================

Ce module étend adi_stock_transfer pour ajouter la réservation automatique
multi-emplacement et la restriction des opérations par équipe commerciale.

Fonctionnalités:
----------------
* Réservation automatique dans les sous-emplacements
* Calcul de disponibilité incluant tous les emplacements enfants
* Traçabilité des emplacements sources utilisés
* Compatibilité avec les transferts existants (mode legacy)
* Priorité des emplacements configurable (alphabétique, création)

Restriction par Équipe (configurable):
--------------------------------------
* Seuls les membres de l'équipe source peuvent envoyer
* Seuls les membres de l'équipe destination peuvent réceptionner
* Les Managers de Transfert peuvent effectuer toutes les opérations
* Liaison automatique équipe-entrepôt

Configuration:
--------------
Menu Configuration dans l'app Transfert:
* Paramètres: activer/désactiver la restriction par équipe
* Équipes: gérer les équipes commerciales
* Utilisateurs: gérer les utilisateurs de transfert
    """,
    'author': 'ADICOPS',
    'website': 'https://www.adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'adi_stock_transfer',
        'crm',  # Pour les équipes commerciales (crm.team)
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_transfer_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
