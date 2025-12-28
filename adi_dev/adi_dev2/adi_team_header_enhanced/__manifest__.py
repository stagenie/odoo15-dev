# -*- coding: utf-8 -*-
{
    'name': 'En-tête Améliorée - AB Energie',
    'version': '15.0.1.0.0',
    'sequence': 2,
    'category': 'Sales',
    'summary': 'Amélioration de l\'affichage de l\'en-tête des rapports',
    'description': """
En-tête Améliorée - AB Energie
==============================

Ce module améliore l'affichage de l'en-tête des rapports :

* Activité commerciale en premier (mise en valeur)
* Adresse de l'entreprise
* Coordonnées fiscales en taille réduite (RC, AI, NIF, NIS)
* Email et téléphone avec icônes

Structure de l'en-tête :
------------------------
1. ACTIVITÉ COMMERCIALE (en gras, bien visible)
2. Adresse complète
3. Coordonnées fiscales (taille réduite)
4. Email et Téléphone
    """,
    'author': 'ADI',
    'website': 'https://www.adi.com',
    'license': 'LGPL-3',
    'depends': [
        'adi_team_header',
    ],
    'data': [
        'views/report_header_enhanced.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
