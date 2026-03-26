# -*- coding: utf-8 -*-
from odoo import models, fields


class InvoicePrintWarningWizard(models.TransientModel):
    _inherit = 'invoice.print.warning.wizard'

    report_xmlid = fields.Char(string='Report XMLID')

    def action_confirm_print(self):
        """Confirmer l'impression en utilisant le bon rapport"""
        self.ensure_one()
        if self.report_xmlid:
            return self.env.ref(self.report_xmlid).report_action(self.invoice_id)
        return super().action_confirm_print()
