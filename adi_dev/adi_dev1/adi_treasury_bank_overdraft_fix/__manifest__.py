# -*- coding: utf-8 -*-
{
    'name': "Trésorerie Banque - Fix faux « Découvert dépassé »",
    'version': '15.0.1.0.0',
    'summary': "Corrige la double déduction du montant dans le contrôle de découvert "
               "des sorties bancaires (adi_treasury_transfer_control).",
    'description': """
Correctif : faux blocage « DÉCOUVERT DÉPASSÉ » sur les sorties bancaires
========================================================================

Problème
--------
adi_treasury_transfer_control redéfinit la contrainte
treasury.bank.operation._check_bank_balance_on_out ainsi :

    current_balance = bank.current_balance
    balance_after   = current_balance - operation.amount

Or `treasury.bank.current_balance` est un champ calculé STOCKÉ, alimenté par
les opérations à l'état 'posted'. Les contraintes Odoo étant évaluées APRÈS le
recalcul des champs stockés, `current_balance` contient déjà le montant de
l'opération en cours. Le montant est donc retranché une seconde fois.

Conséquence : toute sortie supérieure à la moitié du solde disponible est
refusée à tort, avec un message affichant un solde erroné.

Exemple constaté (BANQUE SGA) :
    Solde réel avant           : 17 196 109,49 DA
    Paiement fournisseur       : 10 148 686,25 DA
    « Solde actuel » affiché   :  7 047 423,24 DA  (déjà net de l'opération)
    « Solde après opération »  : -3 101 263,01 DA  (déduit une 2e fois)
Le solde réel après opération est 7 047 423,24 DA : aucun découvert.

Correctif (sans modifier adi_treasury_transfer_control)
-------------------------------------------------------
La contrainte est redéfinie avec la bonne convention, identique à celle du
module de base adi_treasury_bank._check_bank_balance :

    balance_after  = bank.current_balance        (déjà net de l'opération)
    balance_before = balance_after + amount      (solde avant opération)

Le contrôle du découvert et le message restent inchangés ; seuls les montants
comparés et affichés sont corrigés. La branche « solde négatif non autorisé »
est corrigée de la même façon.
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
