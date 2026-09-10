# -*- coding: utf-8 -*-
{
    'name': "Trésorerie Banque - Fix AttributeError 'communication'",
    'version': '15.0.1.0.0',
    'summary': "Corrige l'erreur \"'account.payment' object has no attribute "
               "'communication'\" au chargement des opérations d'un rapprochement bancaire.",
    'description': """
Correctif : AttributeError 'communication' sur account.payment
==============================================================

Problème
--------
Le module adi_treasury_bank construit la description des opérations bancaires ainsi :

    'description': payment.ref or payment.communication or _('Paiement %s') % payment.name

Or le champ 'communication' n'existe plus sur account.payment depuis Odoo 14
(fusion account.payment / account.move) : il a été remplacé par 'ref' et
'payment_reference'.

Grâce au court-circuit de l'opérateur 'or', l'expression ne pose problème que
lorsque 'ref' est vide. Dans ce cas, Odoo lève :

    AttributeError: 'account.payment' object has no attribute 'communication'

L'erreur se déclenche notamment sur le bouton "Charger opérations" d'un
rapprochement bancaire (treasury.bank.closing._sync_payments_to_operations),
et à la validation d'un paiement sans référence
(adi_treasury_bank/models/account_payment.py).

Correctif (sans modifier le module adi_treasury_bank)
-----------------------------------------------------
Réexposition d'un champ de compatibilité 'communication' sur account.payment,
related en lecture seule vers 'payment_reference' (non stocké, aucune colonne
ajoutée en base). Les deux appels existants deviennent valides et retombent
proprement sur 'Paiement <nom>' lorsque aucune référence n'est renseignée.
    """,
    'author': 'ADI',
    'category': 'Accounting',
    'license': 'LGPL-3',
    'depends': [
        'adi_treasury_bank',
    ],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
