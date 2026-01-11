# -*- coding: utf-8 -*-

from odoo import models, api


class ReportInvoiceNoPayment(models.AbstractModel):
    _name = 'report.adi_ab_invoice_reports.ab_report_invoice_no_payment'
    _description = 'Rapport Facture Sans Paiement'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Retourne les valeurs du rapport avec no_payment_report=True"""
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'no_payment_report': True,  # Variable pour masquer les paiements
        }
