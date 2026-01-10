# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class InvoiceLine(models.Model):
    _inherit = 'account.move.line'

    state = fields.Selection(
        related="move_id.state",
        string="State",
        store=True
    )
    inv_type = fields.Selection(
        related="move_id.move_type",
        string="Type",
        store=True
    )
