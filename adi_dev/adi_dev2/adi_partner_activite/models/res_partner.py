# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    activite = fields.Char(
        string="Activit\u00e9",
        help="Activit\u00e9 du client ou fournisseur",
    )
