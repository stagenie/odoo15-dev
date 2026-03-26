from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_status = fields.Selection([
        ('no', 'Non Livré'),
        ('partial', 'Partiellement Livré'),
        ('full', 'Livré'),
    ], string='Statut de Livraison', compute='_compute_delivery_status',
        store=True, default='no')

    @api.depends('state', 'order_line.qty_delivered', 'order_line.product_uom_qty')
    def _compute_delivery_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('sale', 'done'):
                order.delivery_status = 'no'
                continue

            storable_lines = order.order_line.filtered(
                lambda l: l.product_id.type == 'product' and not l.display_type
            )
            if not storable_lines:
                order.delivery_status = 'no'
                continue

            all_delivered = all(
                float_compare(line.qty_delivered, line.product_uom_qty,
                              precision_digits=precision) >= 0
                for line in storable_lines
            )
            any_delivered = any(
                not float_is_zero(line.qty_delivered, precision_digits=precision)
                for line in storable_lines
            )

            if all_delivered:
                order.delivery_status = 'full'
            elif any_delivered:
                order.delivery_status = 'partial'
            else:
                order.delivery_status = 'no'
