# -*- coding: utf-8 -*-
{
    'name': 'Treasury Access Control',
    'version': '15.0.1.7.0',
    'category': 'Accounting/Treasury',
    'summary': 'Gestion des accès, visibilité et protection des opérations de trésorerie',
    'description': """
Treasury Access Control - Contrôle des Accès Trésorerie
========================================================

Ce module gère les droits d'accès et la visibilité des éléments de trésorerie :

Fonctionnalités :
-----------------
* Règles d'accès par utilisateur pour :
  - Caisses (treasury.cash)
  - Coffres (treasury.safe)
  - Banques (treasury.bank)
  - Opérations de caisse/coffre/banque
  - Transferts

* Menus dynamiques :
  - Menu "Caisses" visible si l'utilisateur a au moins une caisse
  - Menu "Coffres" visible si l'utilisateur a au moins un coffre
  - Menu "Banques" visible si l'utilisateur a au moins une banque

* Filtres automatiques :
  - Affichage uniquement des entités autorisées
  - Domaines dynamiques sur les champs relationnels

* Protection des opérations (v1.7.0) :
  - Interdiction de supprimer les opérations dans une clôture validée
  - Interdiction de supprimer les opérations comptabilisées
  - Bouton "Remettre en brouillon" pour permettre la suppression
  - Protection des opérations liées aux transferts et paiements

Principe :
----------
Un utilisateur ne voit QUE les caisses/coffres/banques où il est :
- Dans la liste des utilisateurs autorisés (user_ids)
- Le responsable (responsible_id / responsible_ids)
- Le créateur (create_uid)

Les managers ont accès à tout.
    """,
    'author': 'ADI',
    'website': 'https://www.adi.com',
    'depends': [
        'adi_treasury',
        'adi_treasury_bank',
        'adi_treasury_transfer_control',
    ],
    'data': [
        # Sécurité - Droits d'accès et règles
        'security/ir.model.access.csv',
        'security/treasury_access_rules.xml',
        # Vues
        'views/treasury_menus.xml',
        'views/treasury_access_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
