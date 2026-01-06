# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.depends('company_id', 'payment_type')
    def _compute_journal_id(self):
        """Surcharge pour exclure les journaux masqués."""
        for wizard in self:
            domain = [
                ('company_id', '=', wizard.company_id.id),
                ('type', 'in', ('bank', 'cash')),
            ]
            # Ajouter le filtre pour les journaux masqués
            if not self.env.user.has_group('adi_journal_visibility.group_see_hidden_journals'):
                domain.append(('is_hidden', '=', False))

            journal = self.env['account.journal'].search(domain, limit=1)
            wizard.journal_id = journal


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def _get_default_journal(self):
        """Surcharge pour exclure les journaux masqués du journal par défaut."""
        journal = super()._get_default_journal()
        if journal and journal.is_hidden:
            if not self.env.user.has_group('adi_journal_visibility.group_see_hidden_journals'):
                # Chercher un autre journal non masqué
                domain = [
                    ('company_id', '=', journal.company_id.id),
                    ('type', '=', journal.type),
                    ('is_hidden', '=', False),
                ]
                journal = self.env['account.journal'].search(domain, limit=1)
        return journal
