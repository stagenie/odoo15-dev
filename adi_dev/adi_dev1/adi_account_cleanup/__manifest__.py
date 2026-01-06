# -*- coding: utf-8 -*-
{
    'name': 'Nettoyage Comptable - Gestion des Ecritures Orphelines',
    'version': '15.0.1.0.1',
    'category': 'Accounting/Accounting',
    'summary': 'Detecter et corriger les ecritures orphelines, supprimer les documents annules',
    'description': """
Module de Nettoyage Comptable
=============================

Ce module permet de detecter et corriger les ecritures comptables orphelines
et de nettoyer les documents annules de la base de donnees.

**Fonctionnalites:**

* Detection des ecritures orphelines (referencant des paiements supprimes)
* Contre-passation automatique des ecritures orphelines
* Suppression des paiements annules avec leurs ecritures comptables
* Suppression des factures annulees avec leurs ecritures comptables
* Tableau de bord de nettoyage comptable

**Cas d'utilisation:**

* Ecritures de transfert de caisse restees apres suppression d'un paiement
* Paiements annules qui encombrent la base de donnees
* Factures annulees avec ecritures comptables residuelles

**Securite:**

* Seuls les utilisateurs avec le role "Conseiller comptable" peuvent
  effectuer les operations de nettoyage
* Toutes les operations sont tracees dans le log

**ATTENTION:** Les operations de suppression sont IRREVERSIBLES.
Il est fortement recommande de faire une sauvegarde de la base de donnees
avant d'effectuer des operations de nettoyage.
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'email': 'info@adicops.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/orphan_entries_wizard_views.xml',
        'wizard/cleanup_cancelled_wizard_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
