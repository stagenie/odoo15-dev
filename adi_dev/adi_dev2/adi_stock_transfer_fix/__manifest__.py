# -*- coding: utf-8 -*-
{
    'name': 'ADI Stock Transfer Fix',
    'version': '15.0.2.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Outil de correction des transferts et pickings bloqués',
    'description': """
ADI Stock Transfer Fix
======================

Module utilitaire pour identifier et corriger:
- Les transferts inter-dépôts bloqués (état incohérent)
- Les pickings Odoo natifs bloqués (stock insuffisant)

ORDRE D'INSTALLATION IMPORTANT:
-------------------------------
1. Installer ce module (adi_stock_transfer_fix) EN PREMIER
2. Corriger TOUS les transferts bloqués existants
3. Installer ensuite adi_stock_transfer_enhanced pour prévenir les futurs blocages
4. Garder les deux modules actifs

Voir doc/GUIDE_CORRECTION_TRANSFERTS.md pour la démarche complète.

Fonctionnalités Transferts:
---------------------------
* Détection des transferts "en transit" avec picking non validé
* Diagnostic détaillé des lignes problématiques
* Correction automatique (validation picking avec skip_backorder)
* Historique des corrections

Fonctionnalités Pickings:
-------------------------
* Détection des pickings avec stock source insuffisant
* Détection des stocks négatifs
* 3 options de correction:
  - Ajuster les quantités aux disponibilités
  - Corriger les stocks négatifs
  - Forcer la validation (attention: peut créer du stock négatif)

Utilisation:
------------
1. Aller dans Transferts > Configuration
2. "Détecter les Transferts Bloqués" ou "Détecter les Pickings Bloqués"
3. Visualiser les problèmes dans "Transferts Bloqués" ou "Pickings Bloqués"
4. Analyser et corriger chaque élément
    """,
    'author': 'ADICOPS',
    'website': 'https://www.adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'adi_stock_transfer',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_transfer_fix_views.xml',
        'views/stock_picking_fix_views.xml',
        'wizard/stock_transfer_fix_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
