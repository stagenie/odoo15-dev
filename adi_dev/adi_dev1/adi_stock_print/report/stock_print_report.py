# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.tools.misc import formatLang


class StockPrintReport(models.AbstractModel):
    _name = 'report.adi_stock_print.report_stock_print_document'
    _description = 'Rapport d\'impression du stock'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Récupère les valeurs pour le rapport"""
        wizard = self.env['stock.print.wizard'].browse(docids)

        if not wizard.exists():
            return {
                'doc_ids': docids,
                'docs': wizard,
                'data': data or {},
                'formatLang': lambda value, digits=2, currency_obj=None: formatLang(
                    self.env, value, digits=digits, currency_obj=currency_obj
                ),
            }

        report_data = wizard._prepare_report_data()

        return {
            'doc_ids': docids,
            'docs': wizard,
            'data': report_data,
            'formatLang': lambda value, digits=2, currency_obj=None: formatLang(
                self.env, value, digits=digits, currency_obj=currency_obj
            ),
        }
