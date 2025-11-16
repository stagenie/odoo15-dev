from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    total_discount = fields.Monetary(string='Total des remises', compute='_compute_total_discount', store=True)
    
    @api.depends('order_line.discount', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_total_discount(self):
        for order in self:
            total_discount = 0.0
            for line in order.order_line:
                # Calcul du montant de remise par ligne
                discount_amount = (line.price_unit * line.product_uom_qty) * (line.discount / 100)
                total_discount += discount_amount
            order.total_discount = total_discount