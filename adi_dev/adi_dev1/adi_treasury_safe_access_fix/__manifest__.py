# -*- coding: utf-8 -*-
{
    'name': "Trésorerie - Fix accès coffres par responsables",
    'version': '15.0.1.0.0',
    'summary': "Restreint la lecture des coffres (treasury.safe) au champ Responsables, "
               "y compris pour les managers, sans retirer leurs droits CRUD.",
    'description': """
Correctif de sécurité sur les coffres-forts (treasury.safe)
===========================================================

Problème
--------
La règle "Coffres : accès total pour managers" (adi_treasury.treasury_safe_rule_manager)
utilise le domaine [(1, '=', 1)] avec lecture autorisée, ce qui rend TOUS les coffres
visibles à tout membre du groupe Trésorerie/Manager, en ignorant le champ Responsables.

Correctif (sans modifier le module adi_treasury)
------------------------------------------------
1. La règle de lecture par responsables (adi_treasury.treasury_safe_rule_user) est
   désormais appliquée AUSSI au groupe Manager : la visibilité d'un coffre dépend du
   champ Responsables (responsible_ids) ou de son créateur.
2. La règle manager garde perm_write / perm_create / perm_unlink (les rôles globaux et
   pouvoirs CRUD des managers sont conservés) mais perd perm_read : plus de lecture
   globale de tous les coffres.

Résultat : un manager ne voit que les coffres dont il est responsable (ou créateur),
tout en conservant ses droits d'écriture/création/suppression.
    """,
    'author': 'ADI',
    'category': 'Accounting',
    'license': 'LGPL-3',
    'depends': [
        'adi_treasury',
    ],
    'data': [
        'security/treasury_safe_access_fix.xml',
        'views/treasury_safe_fix_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
