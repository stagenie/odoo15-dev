# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def action_view_product_history(self):
        """Surcharge pour configurer le domaine des clients disponibles"""
        self.ensure_one()

        current_line_id = self.id if self.id else -1

        # Rechercher tout l'historique pour ce produit
        domain = [
            ('product_id', '=', self.product_id.id),
            ('id', '!=', current_line_id)
        ]

        historical_sales = self.env['sale.order.line'].sudo().search(domain, order='create_date desc')

        # Récupérer tous les partenaires uniques
        all_partners = historical_sales.mapped('order_id.partner_id')

        # Créer le wizard
        wizard_vals = {
            'product_id': self.product_id.id,
            'available_partner_ids': [(6, 0, all_partners.ids)],
            'active_line_id': current_line_id,
            'state': False,  # Pas de filtre état par défaut - affiche tous les états
            'sale_history_ids': [(0, 0, {
                'order_id': line.order_id.id,
                'date_order': line.order_id.date_order,
                'partner_id': line.order_id.partner_id.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'salesperson_id': line.order_id.user_id.id,
                'team_id': line.order_id.team_id.id,
                'state': line.order_id.state,
            }) for line in historical_sales]
        }

        wizard = self.env['product.sale.history.wizard'].with_context(
            active_line_id=current_line_id
        ).create(wizard_vals)

        return {
            'name': 'Historique des prix de vente',
            'type': 'ir.actions.act_window',
            'res_model': 'product.sale.history.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_line_id': current_line_id},
        }
