# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResPartner(models.Model):

    _inherit = 'res.partner'


    overdue_amount = fields.Float(compute='_compute_amount', string='Montant Echu')
    balance_due = fields.Float(compute='_compute_amount', string='Total Solde')
    invoice_ids = fields.One2many('account.move', 'partner_id', domain=[('move_type', '=', ('out_invoice')), ('state', '=', 'posted'), ('payment_state', '!=', 'paid')])

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_ids.invoice_date', 'invoice_ids.invoice_date_due')
    def _compute_amount(self):
        account_move_obj = self.env['account.move']
        for record in self:
            current_date = fields.Datetime.now().date()
            total_overdue_amount = 0.0
            total_balance_due = 0.0
            for invoice_id in self.invoice_ids:
                total_balance_due += invoice_id.amount_residual
                if invoice_id.invoice_date_due < current_date:
                    total_overdue_amount += invoice_id.amount_residual
            record.overdue_amount = total_overdue_amount
            record.balance_due = total_balance_due
            