from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    available_journal_ids = fields.Many2many(
        'account.journal',
        compute='_compute_available_journal_ids',
        store=True,
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal de paiement',
        required=True,
        compute='_compute_journal_id',
        store=True,
        readonly=False,
    )

    @api.depends('company_id')
    def _compute_available_journal_ids(self):
        for wizard in self:
            domain = [
                ('company_id', '=', wizard.company_id.id),
                ('type', 'in', ('bank', 'cash'))
            ]
            if self.env.user.journal_ids and not self.env.user.has_group('base.group_system'):
                domain.append(('id', 'in', self.env.user.journal_ids.ids))
            wizard.available_journal_ids = self.env['account.journal'].search(domain)

    @api.depends('company_id', 'available_journal_ids')
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = False
            if wizard.available_journal_ids:
                wizard.journal_id = wizard.available_journal_ids[0]

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type:
            available_journals = self.available_journal_ids.filtered(
                lambda j: j.type in ('bank', 'cash')
            )
            if available_journals:
                self.journal_id = available_journals[0]