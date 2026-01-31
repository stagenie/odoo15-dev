# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    observation = fields.Text(
        string='Observation',
        help="Notes et observations internes sur cette facture"
    )
