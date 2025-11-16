# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError

class AccountGroup(models.Model):
    _inherit = 'account.group'

    @api.depends('account_ids', 'account_ids.debit', 'account_ids.credit', 'account_ids.solde',
                 'group_ids', 'group_ids.debit', 'group_ids.credit', 'account_ids.solde')
    def _compute_debit_credit(self):
        for record in self:
            account_ids = record.account_ids
            group_ids = record.group_ids
            record.debit = sum(account_ids.mapped('debit')) + sum(group_ids.mapped('debit'))
            record.credit = sum(account_ids.mapped('credit')) + sum(group_ids.mapped('credit'))
            record.solde = sum(account_ids.mapped('solde')) + sum(group_ids.mapped('solde'))

    debit = fields.Float(
        string="Débit",
        compute='_compute_debit_credit',
        store=True,
    )

    credit = fields.Float(
        string="Crédit",
        compute='_compute_debit_credit',
        store=True,
    )

    solde = fields.Float(
        string="Solde",
        compute='_compute_debit_credit',
        store=True,
    )

    account_ids = fields.One2many(
        comodel_name='account.account',
        inverse_name='group_id',
        string='Comptes liés'
    )

    group_ids = fields.One2many(
        comodel_name='account.group',
        inverse_name='parent_id',
        string='Groupes liés'
    )

    root_id = fields.Many2one(
        'account.group.root',
        compute='_compute_account_group_root',
        store=True
    )

    @api.depends('code_prefix_start')
    def _compute_account_group_root(self):
        # this computes the first 2 digits of the account.
        # This field should have been a char, but the aim is to use it in a side panel view with hierarchy, and it's only supported by many2one fields so far.
        # So instead, we make it a many2one to a psql view with what we need as records.
        for record in self:
            record.root_id = (ord(record.code_prefix_start[0]) * 1000 + ord(record.code_prefix_start[1:2] or '\x00')) if record.code_prefix_start else False
