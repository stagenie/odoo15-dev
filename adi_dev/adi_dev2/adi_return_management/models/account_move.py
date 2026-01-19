# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    return_order_id = fields.Many2one(
        'return.order',
        string='Ordre de retour',
        readonly=True,
        copy=False,
        help="Ordre de retour lie a cet avoir"
    )
