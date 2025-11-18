# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    exclude_from_partner_ledger = fields.Boolean(
        string='Exclure du Partner Ledger',
        default=False,
        help="Si coché, cette facture sera exclue du calcul des soldes "
             "dans le rapport Partner Ledger (Grand livre des partenaires).",
        tracking=True,
    )
