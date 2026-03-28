# -*- coding: utf-8 -*-
from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_id', 'order_id.picking_type_id')
    def compute_available_qty(self):
        for line in self:
            if line.product_id:
                warehouse = line.order_id.picking_type_id.warehouse_id
                if warehouse:
                    line.available_qty = self.env['stock.quant']._get_available_quantity(
                        line.product_id, warehouse.lot_stock_id, allow_negative=True)
                else:
                    line.available_qty = line.product_id.qty_available
            else:
                line.available_qty = 0
