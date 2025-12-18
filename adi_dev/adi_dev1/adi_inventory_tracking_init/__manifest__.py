# -*- coding: utf-8 -*-
{
    'name': 'Initialisation Suivi Inventaire',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Rétro-remplir les dates d\'inventaire depuis l\'historique',
    'description': """
Initialisation du Suivi des Inventaires
=======================================

Ce module permet de rétro-remplir les champs de suivi d'inventaire
(last_inventory_date, last_inventory_user_id) à partir des mouvements
d'inventaire historiques.

Utilisation :
-------------
1. Installer ce module
2. Aller dans Inventaire > Configuration > Initialiser Suivi Inventaire
3. Sélectionner la période à traiter
4. Cliquer sur "Initialiser"

Note : Ce module peut être désinstallé après utilisation.
    """,
    'author': 'ADI',
    'depends': ['adi_inventory_tracking'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/inventory_tracking_init_wizard_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
