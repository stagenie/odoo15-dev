from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    #  Affichage du Total Pay
    total_paid = fields.Monetary(
        string='Total payé',
        compute='_compute_total_paid',
        store=True
    )

    @api.depends('amount_residual', 'amount_total_with_timbre')
    def _compute_total_paid(self):
        for record in self:
            # Protection contre CacheMiss
            if not record.exists() or not record.id:
                record.total_paid = 0.0
                continue
                
            # Vérifier si amount_total_with_timbre existe déjà
            try:
                record.total_paid = record.amount_total_with_timbre - record.amount_residual
            except:
                record.total_paid = record.amount_total - record.amount_residual

    #  Affichage du % appliquée 
    timbre_percentage = fields.Char(
        string='Pourcentage du timbre',
        compute='_compute_timbre_percentage'
    )

    @api.depends('amount_total', 'payment_mode_id')
    def _compute_timbre_percentage(self):
        for record in self:
            # Protection contre les problèmes d'initialisation
            if not record.exists() or not record.id:
                record.timbre_percentage = False
                continue
                
            if record.payment_mode_id and record.payment_mode_type == "espece":
                droit_timbre_id = self.env['droit.timbre'].get_droit_timbre(record.company_id)
                if record.amount_total <= droit_timbre_id.seuil_premiere_tranche:
                    percentage = droit_timbre_id.taux_premiere_tranche * 100
                elif record.amount_total <= droit_timbre_id.seuil_deuxieme_tranche:
                    percentage = droit_timbre_id.taux_deuxieme_tranche * 100
                else:
                    percentage = droit_timbre_id.taux_troisieme_tranche * 100
                record.timbre_percentage = f"({percentage}%)"
            else:
                record.timbre_percentage = False

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
        compute='_compute_amount_timbre',
        store=True  # Ajouter le stockage pour éviter les problèmes de calcul
    )

    # si le rapport utilise montant en lettre
    # prendre en compte le timbre
    def get_amount_to_text_dz(self):
        return self.currency_id.amount_to_text_dz(self.amount_total_with_timbre if self.payment_mode_type == 'espece'
                                                                                else self.amount_total)

    def _get_aml_timbre_ids(self):
        droit_timbre_id = self.env['droit.timbre'].get_droit_timbre(self.company_id)
        account_id = droit_timbre_id.account_sale_id if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else droit_timbre_id.account_purchase_id
        return self.line_ids.filtered(lambda aml: aml.account_id == account_id)

    def check_apply_update_lines(self):
        try:
            self.line_ids._check_reconciliation()
            return True
        except:
            return False

    @api.depends('amount_total', 'payment_mode_id')  
    def _compute_amount_timbre(self):
        for record in self:
            # Protection contre CacheMiss lors de la création
            if not record.exists() or not record.id:
                record.amount_timbre = 0.0
                record.amount_total_with_timbre = 0.0
                continue
                
            # Protection si payment_mode_id n'est pas encore défini
            if not hasattr(record, 'payment_mode_id') or not record.payment_mode_id:
                record.amount_timbre = 0.0
                record.amount_total_with_timbre = record.amount_total if hasattr(record, 'amount_total') else 0.0
                continue

            if record.payment_mode_id and record.payment_mode_type == "espece":
                record.amount_timbre = self.env['droit.timbre'].get_montant_timbre(record.amount_total, record.company_id, record.move_type)
                record.amount_total_with_timbre = record.amount_total + record.amount_timbre if record.amount_timbre else record.amount_total
            else:
                record.amount_timbre = 0
                record.amount_total_with_timbre = record.amount_total
                # re initialise l'ecriture comptable du droit de timbre
                if record.check_apply_update_lines():
                    timbre_lines = record._get_aml_timbre_ids()
                    if timbre_lines:
                        timbre_lines.with_context({'check_move_validity': False}).update({'debit': 0.0, 'credit': 0.0})
            
            # Ne recomputer que si l'enregistrement existe complètement
            if record.id and hasattr(record, 'with_context'):
                record.with_context({'check_move_validity': False})._recompute_dynamic_lines()

    # Ajout d'une méthode create pour initialiser correctement amount_total_with_timbre
    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        
        # S'assurer que amount_total_with_timbre est initialisé
        if not hasattr(move, 'amount_total_with_timbre') or move.amount_total_with_timbre == 0.0:
            # Éviter les appels récursifs
            if hasattr(move, 'amount_total'):
                move.amount_total_with_timbre = move.amount_total
                
        return move

    def action_post(self):
        for record in self:
            if record.payment_mode_type != "espece":
                # l'ecriture comptable du droit de timbre n'est plus utile
                timbre_lines = record._get_aml_timbre_ids()
                if timbre_lines:
                    timbre_lines.with_context({'check_move_validity': False}).unlink()

        return super(AccountMove, self).action_post()

    def _recompute_timbre(self):
        self.ensure_one()
        # Vérifier si l'enregistrement existe complètement
        if not self.exists() or not self.id:
            return
            
        if self.payment_mode_id and self.payment_mode_type == 'espece':  
            in_draft_mode = self != self._origin
            create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create

            droit_timbre_id = self.env['droit.timbre'].get_droit_timbre(self.company_id)

            if self.move_type in ('out_invoice', 'out_receipt'):
                curr_line = 'credit'  
                account_timbre_id = droit_timbre_id.account_sale_id
            elif self.move_type in ('in_invoice', 'in_refund', 'in_receipt'):
                curr_line = 'debit'
                account_timbre_id = droit_timbre_id.account_purchase_id
            else:  # Ajout d'un cas par défaut pour out_refund
                curr_line = 'debit'
                account_timbre_id = droit_timbre_id.account_sale_id

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
                curr_line: droit_timbre_id.get_montant_timbre(curr_amount, self.company_id, self.move_type),
            })

            others_lines = self.line_ids.filtered(lambda line: line.account_id != account_timbre_id)
            if not others_lines:
                self.line_ids -= existing_timbre_line

            if in_draft_mode:
                timbre_line._onchange_amount_currency()
                timbre_line._onchange_balance()

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        for move in self:
            # Protection contre les problèmes d'initialisation
            if not move.exists() or not move.id:
                continue
                
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
