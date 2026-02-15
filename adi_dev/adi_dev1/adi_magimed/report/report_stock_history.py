# -*- coding: utf-8 -*-

from odoo import api, models


class ReportStockHistory(models.AbstractModel):
    _name = 'report.adi_magimed.report_stock_history'
    _description = 'Rapport Historique Mouvements Stock'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Priority: history_ids from wizard data, then docids, then env context
        if data and data.get('history_ids'):
            history_ids = data['history_ids']
        elif docids:
            history_ids = docids
        elif data and data.get('context', {}).get('active_ids'):
            history_ids = data['context']['active_ids']
        elif self.env.context.get('active_ids'):
            history_ids = self.env.context['active_ids']
        else:
            history_ids = []

        # Use search instead of browse for SQL view model
        docs = self.env['stock.move.history'].search(
            [('id', 'in', history_ids)], order='date desc'
        )

        return {
            'doc_ids': history_ids,
            'doc_model': 'stock.move.history',
            'docs': docs,
            'data': data or {},
        }


class ReportExpirationAlert(models.AbstractModel):
    _name = 'report.adi_magimed.report_expiration_alert'
    _description = 'Rapport Alertes Expiration'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Priority: lot_ids from wizard data, then docids, then env context
        if data and data.get('lot_ids'):
            lot_ids = data['lot_ids']
        elif docids:
            lot_ids = docids
        elif data and data.get('context', {}).get('active_ids'):
            lot_ids = data['context']['active_ids']
        elif self.env.context.get('active_ids'):
            lot_ids = self.env.context['active_ids']
        else:
            lot_ids = []

        lots = self.env['stock.production.lot'].browse(lot_ids)

        # Force compute of non-stored fields so they resolve in QWeb
        for lot in lots:
            lot.total_qty
            lot.location_qty_info
            lot.product_uom_id

        return {
            'doc_ids': lot_ids,
            'doc_model': 'stock.production.lot',
            'docs': lots,
            'data': data or {},
        }
