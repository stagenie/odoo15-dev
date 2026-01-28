# -*- coding: utf-8 -*-
{
    'name': 'ADI Stock Transfer Enhanced',
    'version': '15.0.3.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Réservation multi-emplacement, restriction par équipe et désactivation des reliquats',
    'description': """
ADI Stock Transfer Enhanced
===========================

Ce module étend adi_stock_transfer pour ajouter la réservation automatique
multi-emplacement, la restriction des opérations par équipe commerciale,
et la possibilité de désactiver les reliquats.

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

Désactivation des Reliquats (configurable):
-------------------------------------------
* Option pour désactiver complètement les reliquats
* Quantités approuvées envoyées et reçues en totalité automatiquement
* Champs qty_sent et qty_received en lecture seule si activé
* N'affecte pas les opérations historiques existantes
* En cas d'écart physique, ajustement manuel d'inventaire

Configuration:
--------------
Menu Configuration dans l'app Transfert:
* Paramètres: restriction par équipe, désactivation des reliquats
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
