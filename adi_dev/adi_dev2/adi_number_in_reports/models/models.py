# models/account_move.py, sale_order.py, purchase_order.py, stock_picking.py, etc.

from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    line_number = fields.Integer(string='N° Ligne', compute='_compute_line_number', store=False)
    
    def _compute_line_number(self):
        for document in self.mapped('move_id'):
            lines = document.line_ids.filtered(lambda l: not l.exclude_from_invoice_tab)
            for i, line in enumerate(lines, 1):
                line.line_number = i

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    line_number = fields.Integer(string='N° Ligne', compute='_compute_line_number', store=False)
    
    def _compute_line_number(self):
        for order in self.mapped('order_id'):
            for i, line in enumerate(order.order_line, 1):
                line.line_number = i

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    line_number = fields.Integer(string='N° Ligne', compute='_compute_line_number', store=False)
    
    def _compute_line_number(self):
        for order in self.mapped('order_id'):
            for i, line in enumerate(order.order_line, 1):
                line.line_number = i

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    line_number = fields.Integer(string='N° Ligne', compute='_compute_line_number', store=False)
    
    def _compute_line_number(self):
        for picking in self.mapped('picking_id'):
            for i, line in enumerate(picking.move_ids_without_package, 1):
                line.line_number = i