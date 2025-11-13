# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    exclude_from_partner_balance = fields.Boolean(
        string='Exclure du solde partenaire',
        default=False,
        tracking=True,
        help="Si coché, cette facture/avoir ne sera pas prise en compte dans le calcul "
             "du solde du client/fournisseur (Partner Ledger, crédit, débit, solde)."
    )

    @api.onchange('exclude_from_partner_balance')
    def _onchange_exclude_from_partner_balance(self):
        """Propage la valeur aux lignes de facture"""
        if self.line_ids:
            for line in self.line_ids:
                if line.account_id.internal_type in ('receivable', 'payable'):
                    line.exclude_from_partner_balance = self.exclude_from_partner_balance
