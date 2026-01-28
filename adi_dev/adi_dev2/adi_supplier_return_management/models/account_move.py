# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    supplier_return_order_id = fields.Many2one(
        'supplier.return.order',
        string='Ordre de retour fournisseur',
        readonly=True,
        copy=False,
        help="Ordre de retour fournisseur lie a cet avoir"
    )
