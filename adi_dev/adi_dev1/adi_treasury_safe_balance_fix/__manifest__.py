# -*- coding: utf-8 -*-
{
    'name': "Trésorerie Coffre - Fix faux « Solde insuffisant »",
    'version': '15.0.1.0.0',
    'summary': "Corrige la double déduction du montant dans le contrôle de solde "
               "des sorties de coffre (adi_treasury_transfer_control).",
    'description': """
Correctif : faux blocage « SOLDE INSUFFISANT » sur les sorties de coffre
=======================================================================

Problème
--------
adi_treasury_transfer_control ajoute la contrainte
treasury.safe.operation._check_safe_balance_on_out, évaluée aux états
'confirmed' ET 'done' :

    if current_balance < operation.amount: raise ...

Or `treasury.safe.current_balance` est un champ calculé STOCKÉ, alimenté par
les opérations à l'état 'done'. Lors du passage à 'done', le solde est
recalculé AVANT l'évaluation de la contrainte : il contient déjà la sortie en
cours, qui est donc retranchée une seconde fois.

Conséquence : toute sortie supérieure à la moitié du solde du coffre est
refusée à tort au moment de « Effectuer ».

Exemple constaté (COFFRE PRINCIPAL, OP/2026/00055, 00056, 00058) :
    Solde réel avant           : 5 170 000,00 DA
    Sortie manuelle            : 3 000 000,00 DA
    « Solde actuel » affiché   : 2 170 000,00 DA  (déjà net de l'opération)
    « Manque »                 :   830 000,00 DA  (faux)

Correctif (sans modifier adi_treasury_transfer_control)
-------------------------------------------------------
La contrainte est redéfinie en tenant compte de l'état :
  - 'confirmed' : le solde n'inclut pas encore la sortie
                  -> refus si current_balance < amount
  - 'done'      : le solde inclut déjà la sortie
                  -> refus si current_balance < 0
Le message affiche le solde avant opération. Les contrôles de action_confirm
et action_done (exécutés avant le changement d'état) étaient corrects et
restent inchangés.
    """,
    'author': 'ADI',
    'category': 'Accounting/Treasury',
    'license': 'LGPL-3',
    'depends': [
        'adi_treasury_transfer_control',
    ],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
