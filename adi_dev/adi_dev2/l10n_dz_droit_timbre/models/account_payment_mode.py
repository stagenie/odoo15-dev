from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPaymentMode(models.Model):
    _name = 'account.payment.mode'

    name = fields.Char(
        string='Mode de règlement',
    )

    type = fields.Selection([
        ('espece', 'Espèce'),
        ('banque', 'Banque'),
        ('electronique', 'Électronique'),
        ], string="Type",
    )


