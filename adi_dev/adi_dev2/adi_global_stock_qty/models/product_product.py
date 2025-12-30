# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    global_qty_available = fields.Float(
        string='Qté Totale Disponible',
        compute='_compute_global_qty_available',
        digits='Product Unit of Measure',
        help="Quantité totale disponible dans tous les emplacements de stock "
             "(bypass des restrictions d'emplacement). Lecture seule.",
    )

    def _compute_global_qty_available(self):
        """
        Calcule la quantité totale disponible en utilisant sudo() pour
        bypasser les restrictions d'emplacement (ir.rules).

        Seule la quantité totale est exposée, pas les détails par emplacement.
        """
        for product in self:
            # Utiliser sudo() pour bypasser les ir.rules sur stock.quant
            quants = self.env['stock.quant'].sudo().search([
                ('product_id', '=', product.id),
                ('location_id.usage', '=', 'internal'),  # Emplacements internes uniquement
            ])
            # Calculer la quantité totale (quantity - reserved_quantity = disponible)
            total_qty = sum(quant.quantity - quant.reserved_quantity for quant in quants)
            product.global_qty_available = total_qty
