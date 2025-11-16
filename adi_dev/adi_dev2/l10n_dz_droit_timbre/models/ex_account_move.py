from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'


  


    def _get_name_invoice_report_adi(self):

        """ This method need to be inherit by the localizations if they want to print a custom invoice report instead of
        the default one. For example please review the l10n_ar module """
        self.ensure_one()
        return 'l10n_dz_droit_timbre.adi_report_invoice_document'

    def _get_name_invoice_report_bl_adi(self):

        """ This method need to be inherit by the localizations if they want to print a custom invoice report instead of
        the default one. For example please review the l10n_ar module """
        self.ensure_one()
        return 'l10n_dz_droit_timbre.adi_bl_report_invoice_document'


    payment_mode_id = fields.Many2one(
        'account.payment.mode',
        string="Mode de règlement"
    )

    payment_mode_type = fields.Selection(
        string='Type du mode de règlement',
        related='payment_mode_id.type'
    )

    amount_timbre = fields.Monetary(
        string='Droit de timbre',
        readonly=True,
        compute='_compute_amount_timbre'
    )

    amount_total_with_timbre = fields.Monetary(
        string='Total avec timbre',
        readonly=True,
        compute='_compute_amount_timbre'
    )

    # si le rapport utilise montant en lettre
    # prendre en compte le timbre
    def get_amount_to_text_dz(self):
        return self.currency_id.amount_to_text_dz(self.amount_total_with_timbre if self.payment_mode_type == 'espece'
                                                                                else self.amount_total)

    def _get_aml_timbre_ids(self):
        droit_timbre_id = self.env['droit.timbre'].get_droit_timbre(self.company_id)
        return self.line_ids.filtered(lambda aml: aml.account_id in (droit_timbre_id.account_sale_id, droit_timbre_id.account_purchase_id))

    def check_apply_update_lines(self):
        try:
            self.line_ids._check_reconciliation()
            return True
        except:
            return False

    @api.depends('amount_total', 'payment_mode_id')
    def _compute_amount_timbre(self):
        for record in self:
            if record.payment_mode_id and record.payment_mode_type == "espece":
                record.amount_timbre = self.env['droit.timbre'].get_montant_timbre(record.amount_total, record.company_id)
                record.amount_total_with_timbre = record.amount_total + record.amount_timbre if record.amount_timbre else 0
            else:
                record.amount_timbre = record.amount_total_with_timbre = 0
                # re initialise l'ecriture comptable du droit de timbre
                if record.check_apply_update_lines():
                    record._get_aml_timbre_ids().with_context({'check_move_validity': False}).update({'debit': 0.0, 'credit': 0.0})
            record.with_context({'check_move_validity': False})._recompute_dynamic_lines()

    def action_post(self):
        for record in self:
            if record.payment_mode_type != "espece":
                # l'ecriture comptable du droit de timbre n'est plus utile
                record._get_aml_timbre_ids().with_context({'check_move_validity': False}).unlink()

        return super(AccountMove, self).action_post()

    def _recompute_timbre(self):
        self.ensure_one()
        if self.payment_mode_id and self.payment_mode_type == 'espece':
            in_draft_mode = self != self._origin
            create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create

            droit_timbre_id = self.env['droit.timbre'].get_droit_timbre(self.company_id)

            if self.move_type in ('out_invoice', 'in_invoice', 'out_receipt'):
                curr_line = 'credit'
                account_timbre_id = droit_timbre_id.account_sale_id
            elif self.move_type in ('out_refund', 'in_refund', 'in_receipt'):
                curr_line = 'debit'
                account_timbre_id = droit_timbre_id.account_purchase_id

            timbre_line_vals = {
                'name': 'Droit de timbre',
                'quantity': 1.0,
                'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
                'account_id': account_timbre_id.id,
                'move_id': self.id,
                'partner_id': self.partner_id.id,
                'exclude_from_invoice_tab': True,
            }

            existing_timbre_line = self.line_ids.filtered(lambda line: line.account_id == account_timbre_id)
            timbre_line = create_method(timbre_line_vals) if not existing_timbre_line else existing_timbre_line

            existing_lines = self.line_ids.filtered(lambda line: line.account_id != account_timbre_id and \
                                                                 line.account_id.user_type_id.type not in ('receivable', 'payable'))

            curr_amount = sum(existing_lines.mapped(curr_line))
            timbre_line.update({
                curr_line: droit_timbre_id.get_montant_timbre(curr_amount),
            })

            others_lines = self.line_ids.filtered(lambda line: line.account_id != account_timbre_id)
            if not others_lines:
                self.line_ids -= existing_timbre_line

            if in_draft_mode:
                timbre_line._onchange_amount_currency()
                timbre_line._onchange_balance()

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        for move in self:
            # verifier la/les taxe(s) avant calcule/recalcule du timbre
            for line in move.line_ids:
                if line.recompute_tax_line:
                    recompute_all_taxes = True
                    line.recompute_tax_line = False
                if recompute_all_taxes:
                    move._recompute_tax_lines()
                if recompute_tax_base_amount:
                    move._recompute_tax_lines(recompute_tax_base_amount=True)

            if move.is_invoice(include_receipts=True):
                move._recompute_timbre()

        return super(AccountMove, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)