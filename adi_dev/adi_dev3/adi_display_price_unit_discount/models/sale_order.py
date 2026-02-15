from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_after_discount = fields.Float(
        string="Prix Unitaire Après Remise",
        compute="_compute_price_unit_after_discount",
        store=True
    )

    @api.depends('price_unit', 'discount')
    def _compute_price_unit_after_discount(self):
        for line in self:
            line.price_unit_after_discount = line.price_unit * (1 - (line.discount / 100))



    def _prepare_invoice_line(self, **optional_values):
        values = super()._prepare_invoice_line(**optional_values)
        values['price_unit_after_discount'] = self.price_unit_after_discount
        return values

    has_discount = fields.Boolean(
        string="Has Discount",
        compute="_compute_has_discount",
        store=True
    )

    @api.depends("order_id.has_discount")
    def _compute_has_discount(self):
        for line in self:
            line.has_discount = line.order_id.has_discount



class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_discount = fields.Boolean(
        string="Has Discount", compute="_compute_has_discount", store=True
    )

    @api.depends("order_line.discount")
    def _compute_has_discount(self):
        for order in self:
            order.has_discount = any(line.discount > 0 for line in order.order_line)
    def _prepare_invoice(self):        
        invoice_vals = super()._prepare_invoice()
        invoice_vals["has_discount"] = self.has_discount
        return invoice_vals

