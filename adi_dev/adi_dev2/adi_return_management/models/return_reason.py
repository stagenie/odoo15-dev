# -*- coding: utf-8 -*-
from odoo import models, fields


class ReturnReason(models.Model):
    _name = 'return.reason'
    _description = 'Raison de retour'
    _order = 'sequence, name'

    name = fields.Char(
        string='Raison',
        required=True,
        translate=True
    )
    code = fields.Char(
        string='Code',
        required=True
    )
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    description = fields.Text(
        string='Description'
    )
