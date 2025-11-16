from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def action_view_product_history(self):
        self.ensure_one()
        
        # Si la ligne n'est pas encore enregistrée, on utilise un ID fictif
        current_line_id = self.id if self.id else -1
        
        # Rechercher l'historique des ventes pour ce produit
        domain = [
            ('product_id', '=', self.product_id.id),
            ('id', '!=', current_line_id)
        ]
        
        historical_sales = self.env['sale.order.line'].sudo().search(domain, order='create_date desc')

        # Créer le wizard avec l'historique
        wizard = self.env['product.sale.history.wizard'].with_context(
            active_line_id=current_line_id
        ).create({
            'product_id': self.product_id.id,
            'sale_history_ids': [(0, 0, {
                'order_id': line.order_id.id,
                'date_order': line.order_id.date_order,
                'price_unit': line.price_unit,
                'discount': line.discount,  # Ajout de la remise
                'salesperson_id': line.order_id.user_id.id,
                'team_id': line.order_id.team_id.id,
                'state': line.order_id.state,
            }) for line in historical_sales]
        })

        return {
            'name': 'Historique des prix de vente',
            'type': 'ir.actions.act_window',
            'res_model': 'product.sale.history.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }