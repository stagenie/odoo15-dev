# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    exclude_from_invoice_tab = fields.Boolean(
        string="Ne pas proposer pour régler les factures",
        default=False,
        help="Si coché, cette ligne ne sera pas proposée dans le widget "
             "de rapprochement en bas des factures.",
    )

    def action_exclude_from_invoice_tab(self):
        """Appelé par le widget JS pour exclure une ligne du rapprochement."""
        self.write({'exclude_from_invoice_tab': True})
        # Synchroniser vers le paiement associé si existant
        for line in self:
            if line.payment_id and not line.payment_id.exclude_from_invoice_tab:
                line.payment_id.exclude_from_invoice_tab = True
