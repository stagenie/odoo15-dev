# -*- coding: utf-8 -*-
{
    'name': "Trésorerie Coffre - Fix affichage Solde avant / après",
    'version': '15.0.1.0.0',
    'summary': "Corrige les soldes avant/après affichés sur les opérations de coffre.",
    'description': """
Correctif : soldes avant / après faux sur les opérations de coffre
==================================================================

Problème
--------
adi_treasury calcule (champs non stockés) :

    balance_before = safe.current_balance          (solde ACTUEL du coffre)
    balance_after  = balance_before -/+ amount     (si état 'done')

Pour une opération effectuée, current_balance inclut déjà l'opération : le
« Solde avant » est en réalité le solde après, et le « Solde après » retranche
le montant une seconde fois. Pour une opération ancienne, c'est le solde du
jour qui est affiché, pas celui de l'époque.

Exemple (COFFRE PRINCIPAL, sortie 3 000 000,00 DA, solde initial 5 170 000,00) :
    affiché : 2 170 000,00 -> -830 000,00
    réel    : 5 170 000,00 -> 2 170 000,00

Correctif (sans modifier adi_treasury)
--------------------------------------
- Brouillon / Confirmé : solde avant = solde actuel du coffre,
  solde après = solde prévu après l'opération.
- Effectué : les soldes réels sont enregistrés au moment de « Effectuer »
  et ne bougent plus.
- Opérations effectuées avant l'installation de ce module, et opérations
  annulées : aucun solde fiable -> la section « Soldes » est masquée.
    """,
    'author': 'ADI',
    'category': 'Accounting/Treasury',
    'license': 'LGPL-3',
    'depends': [
        'adi_treasury',
        'adi_treasury_transfer_control',
    ],
    'data': [
        'views/treasury_safe_operation_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
