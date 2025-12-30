# -*- coding: utf-8 -*-
{
    'name': 'Treasury Enhanced',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Améliorations pour la gestion des clôtures de caisse',
    'description': """
Treasury Enhanced - Gestion Avancée des Clôtures
=================================================

Ce module améliore la gestion des clôtures de caisse avec les fonctionnalités suivantes :

Fonctionnalités :
-----------------
* Affichage des opérations manuelles directement dans le formulaire de clôture :
  - Opérations en brouillon (à valider)
  - Opérations comptabilisées

* Bouton intelligent "Opérations à traiter" :
  - Compteur des opérations en brouillon non encore validées
  - Accès rapide pour consulter, valider ou supprimer

* Actions groupées sur les opérations :
  - Valider toutes les opérations en brouillon
  - Supprimer les opérations en brouillon non nécessaires

* Amélioration du workflow de clôture :
  - Visualisation claire des opérations à traiter
  - Validation simplifiée avant confirmation

Principe :
----------
Avant de confirmer une clôture, l'utilisateur peut :
1. Voir toutes les opérations manuelles de la période
2. Valider (comptabiliser) celles qui sont en brouillon
3. Supprimer les opérations brouillon non nécessaires
4. Confirmer la clôture une fois tout validé
    """,
    'author': 'ADI',
    'website': 'https://www.adi.com',
    'depends': [
        'adi_treasury',
        'adi_treasury_access',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/treasury_cash_closing_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
