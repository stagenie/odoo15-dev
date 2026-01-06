# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    show_payment_details = fields.Boolean(
        string='Afficher détails paiement',
        default=False,
        help="Cocher pour afficher les détails de paiement (mode de règlement, etc.) sur le rapport imprimé."
    )
