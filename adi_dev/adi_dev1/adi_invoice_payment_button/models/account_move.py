# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_count = fields.Integer(
        string='Nombre de paiements',
        compute='_compute_payment_count',
    )
    payment_ids = fields.Many2many(
        'account.payment',
        string='Paiements',
        compute='_compute_payment_ids',
    )

    @api.depends('line_ids.matched_debit_ids', 'line_ids.matched_credit_ids')
    def _compute_payment_ids(self):
        for move in self:
            payments = self.env['account.payment']
            if move.is_invoice():
                # Récupérer les paiements via les reconciliations
                for line in move.line_ids.filtered(
                    lambda l: l.account_id.internal_type in ('receivable', 'payable')
                ):
                    # Paiements via matched_debit_ids
                    for partial in line.matched_debit_ids:
                        if partial.debit_move_id.payment_id:
                            payments |= partial.debit_move_id.payment_id
                        if partial.credit_move_id.payment_id:
                            payments |= partial.credit_move_id.payment_id
                    # Paiements via matched_credit_ids
                    for partial in line.matched_credit_ids:
                        if partial.debit_move_id.payment_id:
                            payments |= partial.debit_move_id.payment_id
                        if partial.credit_move_id.payment_id:
                            payments |= partial.credit_move_id.payment_id
            move.payment_ids = payments

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for move in self:
            move.payment_count = len(move.payment_ids)

    def action_view_payments(self):
        """Ouvre la vue des paiements liés à cette facture"""
        self.ensure_one()
        payments = self.payment_ids

        action = {
            'name': 'Paiements',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }

        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })

        return action
