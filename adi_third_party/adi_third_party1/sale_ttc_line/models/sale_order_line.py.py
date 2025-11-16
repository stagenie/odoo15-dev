from . import sale_order_line

##############################################################################
# models/sale_order_line.py
##############################################################################
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    price_total_with_tax = fields.Monetary(
        string='Montant TTC',
        compute='_compute_price_total_with_tax',
        store=True,
        currency_field='currency_id'
    )
    
    @api.depends('price_subtotal', 'tax_id')
    def _compute_price_total_with_tax(self):
        for line in self:
            # Calcul du montant TTC
            taxes = line.tax_id.compute_all(
                line.price_unit,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id
            )
            line.price_total_with_tax = taxes['total_included']