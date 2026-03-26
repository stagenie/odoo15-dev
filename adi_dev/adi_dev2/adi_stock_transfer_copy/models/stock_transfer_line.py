# -*- coding: utf-8 -*-
from odoo import models


class StockTransferLineCopy(models.Model):
    _inherit = 'adi.stock.transfer.line'

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'qty_sent': 0.0,
            'qty_received': 0.0,
            'source_line_ids': [(5, 0, 0)],
        })
        return super().copy(default=default)
