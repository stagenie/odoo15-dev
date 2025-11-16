from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    total_qty = fields.Float(
        string="Quantité Totale",
        compute="_compute_total_qty",
        store=True,
    )

    @api.depends('stock_quant_ids.quantity')
    def _compute_total_qty(self):
        for product in self:
            # Total des quantités pour ce produit
            total_quantity = sum(
                self.env['stock.quant'].search([('product_id', '=', product.id)]).mapped('quantity')
            )
            product.total_qty = total_quantity

   
class ProductTemplate(models.Model):
    _inherit = "product.template"

    total_qty = fields.Float(
        string="Quantité Totale",
        compute="_compute_total_qty",
        store=True,
    )

    @api.depends('product_variant_ids', 'product_variant_ids.qty_available')
    def _compute_total_qty(self):
        for template in self:
            template.total_qty = sum(template.mapped('product_variant_ids.qty_available'))

    