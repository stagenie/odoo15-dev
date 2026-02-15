# -*- coding: utf-8 -*-
{
    'name': 'Bande Base Démo',
    'version': '15.0.1.0.0',
    'category': 'Tools',
    'summary': 'Affiche une bande rouge "Base Démo" en haut du webclient',
    'description': """
Bande Base Démo
================

Affiche une bande rouge fixe en haut de l'interface web pour indiquer
clairement que la base en cours est une base de démonstration ou de formation.

Configurable via les paramètres système :
- ``web.demo_banner_enabled`` : activer/désactiver la bande
- ``web.demo_banner_text`` : texte affiché dans la bande
    """,
    'author': 'ADICOPS',
    'email': 'info@adicops.com',
    'website': 'https://adicops.com/',
    'depends': ['web'],
    'data': [
        'data/ir_config_parameter.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adi_demo_banner/static/src/js/demo_banner.js',
            'adi_demo_banner/static/src/css/demo_banner.css',
        ],
        'web.assets_qweb': [
            'adi_demo_banner/static/src/xml/demo_banner.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
