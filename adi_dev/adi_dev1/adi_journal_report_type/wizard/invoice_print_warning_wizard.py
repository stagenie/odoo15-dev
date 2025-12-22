# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class InvoicePrintWarningWizard(models.TransientModel):
    _name = 'invoice.print.warning.wizard'
    _description = 'Avertissement impression facture'

    invoice_id = fields.Many2one('account.move', string='Facture', required=True)
    warning_message = fields.Text(string='Message', readonly=True)

    def action_confirm_print(self):
        """Confirmer l'impression malgré l'avertissement"""
        self.ensure_one()
        return self.env.ref('adi_ab_invoice_reports.action_report_ab_invoice').report_action(self.invoice_id)

    def action_cancel(self):
        """Annuler l'impression"""
        return {'type': 'ir.actions.act_window_close'}
