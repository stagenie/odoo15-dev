# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    check_quantity_purchased = fields.Boolean(string="Quantités Achetées F")
    check_quantity_saled = fields.Boolean(string="Quantités Vendues F")