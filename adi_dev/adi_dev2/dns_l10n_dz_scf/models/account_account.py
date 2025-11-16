# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.depends('move_line_ids', 'move_line_ids.debit', 'move_line_ids.credit')
    def _compute_debit_credit(self):
        for record in self:
            record.debit = sum(record.move_line_ids.mapped('debit'))
            record.credit = sum(record.move_line_ids.mapped('credit'))
            record.solde = record.debit - record.credit

            curr_group_id = record.group_id
            group_ids = curr_group_id

            while curr_group_id.parent_id:
                curr_group_id = curr_group_id.parent_id
                group_ids += curr_group_id

            group_ids.sorted(key=lambda group_id: group_id.id, reverse=True)
            group_ids._compute_debit_credit()

    debit = fields.Monetary(
        string="Débit",
        compute='_compute_debit_credit',
        store=True,
    )

    credit = fields.Monetary(
        string="Crédit",
        compute='_compute_debit_credit',
        store=True,
    )

    solde = fields.Monetary(
        string="Solde",
        compute='_compute_debit_credit',
        store=True,
    )

    move_line_ids = fields.One2many(
        string='ecritures comptable',
        comodel_name='account.move.line',
        inverse_name='account_id',
    )
