# -*- coding: utf-8 -*-
{
    'name': 'Suivi Inventaire Stock',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Suivre les articles inventoriés et filtrer par date d\'inventaire',
    'description': """
Suivi des Inventaires Stock
===========================

Ce module permet de :
- Tracer la date du dernier inventaire pour chaque article/emplacement
- Savoir qui a effectué le dernier inventaire
- Filtrer les articles inventoriés / non inventoriés depuis une date donnée
- Identifier rapidement les articles qui n'ont jamais été inventoriés

Fonctionnalités :
-----------------
* Champ "Date dernier inventaire" sur les quants
* Champ "Inventorié par" sur les quants
* Filtres de recherche : Inventorié aujourd'hui, cette semaine, ce mois, jamais inventorié
* Groupement par date d'inventaire
    """,
    'author': 'ADI',
    'website': '',
    'depends': ['stock'],
    'data': [
        'views/stock_quant_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
