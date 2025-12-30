# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    global_qty_available = fields.Float(
        string='Qté Totale Disponible',
        compute='_compute_global_qty_available',
        digits='Product Unit of Measure',
        help="Quantité totale disponible dans tous les emplacements de stock "
             "(bypass des restrictions d'emplacement). Lecture seule.",
    )

    def _compute_global_qty_available(self):
        """
        Calcule la quantité totale disponible pour le template en agrégeant
        toutes les variantes. Utilise sudo() pour bypasser les restrictions.

        Seule la quantité totale est exposée, pas les détails par emplacement.
        """
        for template in self:
            # Récupérer toutes les variantes du template
            variants = template.product_variant_ids
            if variants:
                # Utiliser sudo() pour bypasser les ir.rules sur stock.quant
                quants = self.env['stock.quant'].sudo().search([
                    ('product_id', 'in', variants.ids),
                    ('location_id.usage', '=', 'internal'),  # Emplacements internes uniquement
                ])
                # Calculer la quantité totale disponible
                total_qty = sum(quant.quantity - quant.reserved_quantity for quant in quants)
                template.global_qty_available = total_qty
            else:
                template.global_qty_available = 0.0
