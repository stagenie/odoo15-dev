from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    partner_balance = fields.Monetary(
        string='Solde Actuel',
        compute='_compute_partner_balance',
        currency_field='currency_id',
    )
    partner_old_balance = fields.Monetary(
        string='Ancien Solde',
        compute='_compute_partner_balance',
        currency_field='currency_id',
    )

    @api.depends('partner_id', 'amount', 'payment_type', 'partner_type', 'state')
    def _compute_partner_balance(self):
        for payment in self:
            if not payment.partner_id:
                payment.partner_balance = 0.0
                payment.partner_old_balance = 0.0
                continue

            partner = payment.partner_id
            if payment.partner_type == 'supplier':
                current_balance = partner.debit
            else:
                current_balance = partner.credit

            payment.partner_balance = current_balance

            if payment.state == 'posted':
                payment.partner_old_balance = current_balance + payment.amount
            else:
                payment.partner_old_balance = current_balance
