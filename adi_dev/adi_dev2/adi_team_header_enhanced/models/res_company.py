# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_bank_account = fields.Char(
        string='Compte bancaire par defaut',
        help="Compte bancaire affiche dans l'en-tete des rapports"
    )
