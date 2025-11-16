{
    'name': 'Hide Rainbow Man',
    'version': '15.0.1.0.0',
    'category': 'Tools',
    'summary': 'Masque globalement le Rainbow Man dans Odoo',
    'author': 'Votre Nom',
    'website': 'https://www.votresite.com',
    'license': 'LGPL-3',
    'depends': ['web', 'base_setup'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adi_hide_rainbow/static/src/js/disable_rainbow_man.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}