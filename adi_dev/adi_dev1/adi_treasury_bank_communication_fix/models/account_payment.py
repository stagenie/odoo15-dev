# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Champ de compatibilité : 'communication' a été supprimé d'account.payment
    # depuis Odoo 14 (fusion account.payment / account.move). Le module
    # adi_treasury_bank l'utilise encore comme repli quand 'ref' est vide :
    #   payment.ref or payment.communication or ...
    # Grâce au court-circuit du 'or', l'attribut n'est évalué (et l'AttributeError
    # levée) que pour les paiements dont la référence est vide.
    # On réexpose donc 'communication' en lecture seule sur 'payment_reference',
    # qui porte la même information dans Odoo 15.
    communication = fields.Char(
        string="Communication",
        related='payment_reference',
        readonly=True,
        store=False,
    )
