# -*- coding: utf-8 -*-
{
    'name': 'Contrôle des BL par Équipe Commerciale',
    'version': '15.0.1.0.0',
    'summary': 'Restriction validation BL et modification entrepôt par équipe commerciale',
    'description': """
Contrôle des Bons de Livraison par Équipe Commerciale

Ce module ajoute deux contrôles de sécurité sur les bons de livraison :

1. Validation des BL :
   - Un utilisateur ne peut valider QUE les BL de son équipe commerciale
   - Basé sur l'équipe de la commande de vente liée au BL

2. Modification de l'entrepôt :
   - Un utilisateur ne peut modifier l'entrepôt de livraison que si l'entrepôt
     est dans sa liste d'entrepôts autorisés

Groupe spécial :
Un nouveau groupe "Peut valider les BL de tous les dépôts" permet à certains
utilisateurs (superviseurs, coordinateurs) de contourner ces restrictions.

Compatibilité :
- Utilise la relation existante sale_id sur stock.picking
- S'appuie sur le champ available_warehouse_ids du module warehouse_restrictions_app
    """,
    'category': 'Inventory/Delivery',
    'author': 'ADI',
    'website': 'https://adicops-dz.com',
    'depends': [
        'stock',
        'sale_stock',
        'sales_team',
        'warehouse_restrictions_app',
        'adi_stock_transfer_report',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
