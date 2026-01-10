# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opp_number = fields.Char(
        string='OPP Number',
        help='Numéro OPP du client',
        copy=True,
    )
