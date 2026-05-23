# -*- coding: utf-8 -*-
{
    'name': 'ADI Treasury - Fix Solde Initial Clôture',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': "Correctif solde initial lors de clôtures multiples par jour",
    'description': """
Fix Solde Initial Clôture de Caisse
=====================================

Corrige le bug intermittent où le solde initial d'une nouvelle clôture
ne reprend pas correctement le solde réel de la dernière clôture validée
lorsque plusieurs clôtures existent pour la même journée.

Causes corrigées:
-----------------
1. Ordre de recherche non-déterministe (ajout 'id desc' en tiebreaker)
2. Cache stale après création (invalidate_cache + recompute forcé)
3. Fallback vers cash.last_closing_balance si search échoue
4. Bouton manuel "Recalculer solde initial" sur le formulaire
5. Logs diagnostic [BALANCE_FIX] dans /var/log/odoo
6. Action de réparation données existantes (menu Configuration)
""",
    'author': 'ADI Dev',
    'depends': [
        'adi_treasury',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/treasury_cash_closing_views.xml',
        'wizard/balance_fix_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
