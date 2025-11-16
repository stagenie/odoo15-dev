# __manifest__.py
{
    'name': 'Stock Picking Location View',
    'version': '15.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Affiche les emplacements source et destination en haut du formulaire de transfert',
    'depends': ['stock'],
    'data': [
         'security/security.xml',
         'security/ir.model.access.csv',
         'reports/piching_view.xml',
         'reports/report_stockpicking_operations.xml',
         
    ],
    'sequence' :1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}