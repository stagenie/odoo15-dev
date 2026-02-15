# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    exclude_from_payment_widget = fields.Boolean(
        string="Ne pas proposer pour régler les factures",
        default=False,
        tracking=True,
        help="Si coché, ce paiement ne sera pas proposé dans le widget "
             "de rapprochement en bas des factures.",
    )

    def write(self, vals):
        res = super().write(vals)
        if 'exclude_from_payment_widget' in vals:
            self._sync_exclude_to_move_lines(vals['exclude_from_payment_widget'])
        return res

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)
        for payment, vals in zip(payments, vals_list):
            if vals.get('exclude_from_payment_widget'):
                payment._sync_exclude_to_move_lines(True)
        return payments

    def _sync_exclude_to_move_lines(self, exclude_value):
        """Synchronise la valeur du champ sur les lignes receivable/payable de l'écriture."""
        for payment in self:
            lines = payment.move_id.line_ids.filtered(
                lambda l: l.account_id.user_type_id.type in ('receivable', 'payable')
            )
            if lines:
                lines.write({'exclude_from_payment_widget': exclude_value})
