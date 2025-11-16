from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    price_unit_with_tax = fields.Monetary(
        string='Prix Unitaire TTC',
        compute='_compute_price_with_tax',
        store=True,
        currency_field='currency_id'
    )
    
    price_total_with_tax = fields.Monetary(
        string='Montant TTC',
        compute='_compute_price_with_tax',
        store=True,
        currency_field='currency_id'
    )

    @api.depends('price_unit', 'price_subtotal')
    def _compute_price_with_tax(self):
        for line in self:
            # Application directe de la TVA à 19%
            line.price_unit_with_tax = line.price_unit * 1.19
            line.price_total_with_tax = line.price_subtotal * 1.19

    """
    @api.depends('price_unit', 'tax_id', 'product_uom_qty')
    def _compute_price_with_tax(self):
        for line in self:
            # Calcul des taxes
            taxes = line.tax_id.compute_all(
                line.price_unit,
                line.order_id.currency_id,
                1.0,  # Quantité = 1 pour le prix unitaire
                product=line.product_id,
                partner=line.order_id.partner_shipping_id
            )
            
            # Prix unitaire TTC
            line.price_unit_with_tax = taxes['total_included']
            
            # Montant total TTC (prix unitaire TTC × quantité)
            taxes_total = line.tax_id.compute_all(
                line.price_unit,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id
            )
            line.price_total_with_tax = taxes_total['total_included']
    """
    