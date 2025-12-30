# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    global_qty_available = fields.Float(
        string='Stock Total',
        compute='_compute_global_qty_available',
        digits='Product Unit of Measure',
        help="Quantité totale disponible dans tous les emplacements de stock "
             "(bypass des restrictions d'emplacement). Lecture seule.",
    )

    @api.depends('product_id')
    def _compute_global_qty_available(self):
        """
        Calcule la quantité totale disponible pour le produit de la ligne.
        Utilise sudo() pour bypasser les restrictions d'emplacement.
        """
        for line in self:
            if line.product_id:
                # Utiliser sudo() pour bypasser les ir.rules sur stock.quant
                quants = self.env['stock.quant'].sudo().search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id.usage', '=', 'internal'),
                ])
                total_qty = sum(quant.quantity - quant.reserved_quantity for quant in quants)
                line.global_qty_available = total_qty
            else:
                line.global_qty_available = 0.0
