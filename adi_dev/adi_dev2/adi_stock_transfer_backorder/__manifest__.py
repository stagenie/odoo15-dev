{
    'name': 'ADI Stock Transfer - Backorder Management',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Gestion des reliquats et receptions partielles pour les transferts de stock',
    'description': """
Module complementaire pour la gestion des reliquats de transfert

Fonctionnalites principales:

* Reception partielle des transferts de stock
* Gestion des ecarts entre quantites envoyees et recues
* Options de traitement des reliquats:
  - Retour a l'expediteur
  - Ajustement d'inventaire
  - Report pour envoi ulterieur
* Tracabilite des mouvements de reliquat
* Calcul automatique: reliquat = quantite envoyee - quantite recue

Prerequis: Module adi_stock_transfer
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'depends': ['adi_stock_transfer'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_transfer_receive_wizard_views.xml',
        'views/stock_transfer_backorder_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
