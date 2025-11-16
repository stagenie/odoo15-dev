# -*- coding: utf-8 -*-
{
    'name': 'Mouvements des Produits et despalettes',
    'version': '15.0.0.0',
    'category': 'Account',
    'sequence': 1,
    'author': 'Fawzi',
    'summary': 'Product & Palet Stock Moves',
    'description': """
    
         Afficher les mouvements des Propduits et  palettes 

    """,
    'website': '',
    'depends': [
        'base','product','stock',
	],
    'data': [
        'security/ir.model.access.csv',        
        'reports/products_movements_report.xml',        
        'wizards/products_mouvements_wizard_view.xml',

    ],
    'installable': True,
    'application': False,
}
