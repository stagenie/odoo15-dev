# -*- coding: utf-8 -*-
{
    'name': 'MAGIMED Cleanup - Préparation base ISO',
    'version': '15.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Nettoyage et préparation de la base avant installation adi_magimed',
    'description': """
MAGIMED Cleanup - Préparation base ISO
=======================================

Module à usage unique pour préparer la base dupliquée avant installation
du module adi_magimed (traçabilité lots/ISO).

**Étapes du wizard :**

1. Nettoyer les enregistrements orphelins (move lines, moves, réservations)
2. Terminer toutes les opérations (pickings, inventaires, commandes)
3. Activer le suivi par lot sur tous les produits stockables
4. Remettre le stock (quants) à zéro pour inventaire physique frais

**ATTENTION :** Ce module est à usage UNIQUE sur la base dupliquée.
Les opérations sont IRRÉVERSIBLES.
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'stock',
        'purchase',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cleanup_wizard_views.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
