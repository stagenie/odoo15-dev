from odoo import api, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('partner_id', 'amount', 'payment_type', 'partner_type', 'state')
    def _compute_partner_balance(self):
        has_exclude_field = 'exclude_from_partner_ledger' in self.env['account.move']._fields

        for payment in self:
            if not payment.partner_id:
                payment.partner_balance = 0.0
                payment.partner_old_balance = 0.0
                continue

            domain = [
                ('partner_id', '=', payment.partner_id.id),
                ('move_id.state', '=', 'posted'),
                ('account_id.user_type_id.type', 'in', ['receivable', 'payable']),
            ]
            if has_exclude_field:
                domain.append(('move_id.exclude_from_partner_ledger', '!=', True))

            lines = self.env['account.move.line'].search(domain)
            # balance = debit - credit : positif = créance, négatif = dette
            current_balance = sum(lines.mapped('balance'))

            payment.partner_balance = current_balance

            if payment.state == 'posted':
                if payment.payment_type == 'inbound':
                    # Encaissement : le partenaire nous devait plus avant
                    payment.partner_old_balance = current_balance + payment.amount
                else:
                    # Décaissement : nous devions plus au partenaire avant
                    payment.partner_old_balance = current_balance - payment.amount
            else:
                payment.partner_old_balance = current_balance
