from odoo import models


class TreasuryTransfer(models.Model):
    _inherit = 'treasury.transfer'

    def amount_to_text(self):
        self.ensure_one()
        dz_currency = self.env.ref('base.DZD')
        return dz_currency.amount_to_text_dz(self.amount)
