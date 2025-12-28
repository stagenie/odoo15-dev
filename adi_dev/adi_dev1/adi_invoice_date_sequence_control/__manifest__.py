# -*- coding: utf-8 -*-
{
    'name': 'Contrôle Date/Séquence Facturation',
    'version': '15.0.1.0.0',
    'summary': 'Contrôle la cohérence entre les dates et numéros séquentiels des factures',
    'description': """
Contrôle Date/Séquence Facturation
==================================

Ce module empêche la création de factures avec des dates incohérentes
par rapport à leur numéro séquentiel.

Fonctionnalités :
-----------------
* Contrôle que la date d'une nouvelle facture est supérieure ou égale
  à la date de la dernière facture validée dans le même journal
* Option d'activation/désactivation de la contrainte
* Date d'application configurable (les factures avant cette date ne sont pas contrôlées)
* S'applique aux factures et avoirs clients

Configuration :
---------------
Allez dans Facturation > Configuration > Paramètres pour configurer :
* Activer/Désactiver le contrôle
* Définir la date d'application de la contrainte
    """,
    'author': 'ADI Dev',
    'website': '',
    'category': 'Accounting/Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
