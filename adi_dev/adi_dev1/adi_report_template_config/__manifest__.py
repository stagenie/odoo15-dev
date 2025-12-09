# -*- coding: utf-8 -*-
{
    'name': 'Configuration Templates Rapports',
    'version': '15.0.1.0.0',
    'category': 'Sales/Configuration',
    'summary': 'Configuration avancée des templates de rapports avec styles personnalisables',
    'description': """
Configuration Templates Rapports
================================

Ce module étend adi_team_header pour offrir des options de personnalisation
des rapports sans modifier le module original.

Fonctionnalités :
-----------------
* Choix du style de template : Light, Box, Bold
* Option d'afficher les informations fiscales en pied de page
* Configuration par équipe commerciale
* Configuration globale dans les paramètres de vente

Styles disponibles :
-------------------
* **Light** : Style épuré et minimaliste (style actuel)
* **Box** : Informations dans des cadres avec bordures
* **Bold** : Mise en forme prononcée avec titres en gras

Avantages :
-----------
* Non-destructif : n'écrase pas le module original
* Configurable : l'utilisateur choisit selon ses préférences
* Désinstallable : en cas de problème, retour à l'original
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'adi_team_header',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/report_template_data.xml',
        'views/res_config_settings_views.xml',
        'views/crm_team_views.xml',
        'report/report_layouts.xml',
        'report/report_footer_fiscal.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
