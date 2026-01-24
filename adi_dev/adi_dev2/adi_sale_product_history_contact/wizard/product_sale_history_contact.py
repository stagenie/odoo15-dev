# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductSaleHistoryContact(models.TransientModel):
    _inherit = 'product.sale.history.wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        help="Filtrer par client. Laissez vide pour afficher tous les clients."
    )

    # Champ Many2many pour stocker les partenaires disponibles (ceux qui ont commandé ce produit)
    available_partner_ids = fields.Many2many(
        'res.partner',
        'product_sale_history_wizard_available_partner_rel',
        'wizard_id',
        'partner_id',
        string='Partenaires disponibles',
    )

    # Champ pour stocker l'ID de la ligne active
    active_line_id = fields.Integer(string='Ligne active')

    def action_show_all_partners(self):
        """Bouton pour afficher tous les clients - réinitialise le filtre"""
        self.ensure_one()
        self.partner_id = False

        # Recalculer l'historique sans filtre partenaire
        domain = [
            ('product_id', '=', self.product_id.id),
            ('id', '!=', self.active_line_id or -1)
        ]

        if self.date_from:
            domain.append(('order_id.date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('order_id.date_order', '<=', self.date_to))
        if self.state:
            domain.append(('order_id.state', '=', self.state))
        if self.salesperson_id:
            domain.append(('order_id.user_id', '=', self.salesperson_id.id))
        if self.team_id:
            domain.append(('order_id.team_id', '=', self.team_id.id))

        historical_sales = self.env['sale.order.line'].sudo().search(domain, order='create_date desc')

        # Mettre à jour les lignes
        self.sale_history_ids.unlink()
        vals = []
        for line in historical_sales:
            vals.append((0, 0, {
                'order_id': line.order_id.id,
                'date_order': line.order_id.date_order,
                'partner_id': line.order_id.partner_id.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'salesperson_id': line.order_id.user_id.id,
                'team_id': line.order_id.team_id.id,
                'state': line.order_id.state,
            }))
        self.sale_history_ids = vals

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.sale.history.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.onchange('date_from', 'date_to', 'state', 'salesperson_id', 'team_id', 'partner_id')
    def _onchange_filters(self):
        """Surcharge pour ajouter le filtre par client"""
        domain = [
            ('product_id', '=', self.product_id.id),
            ('id', '!=', self.active_line_id or self._context.get('active_line_id', -1))
        ]

        # Filtre par client SEULEMENT si un client est sélectionné
        if self.partner_id:
            domain.append(('order_id.partner_id', '=', self.partner_id.id))

        if self.date_from:
            domain.append(('order_id.date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('order_id.date_order', '<=', self.date_to))
        if self.state:
            domain.append(('order_id.state', '=', self.state))
        if self.salesperson_id:
            domain.append(('order_id.user_id', '=', self.salesperson_id.id))
        if self.team_id:
            domain.append(('order_id.team_id', '=', self.team_id.id))

        historical_sales = self.env['sale.order.line'].sudo().search(domain, order='create_date desc')

        # Supprime les anciennes lignes
        self.sale_history_ids.unlink()

        # Crée les nouvelles lignes filtrées
        vals = []
        for line in historical_sales:
            vals.append((0, 0, {
                'order_id': line.order_id.id,
                'date_order': line.order_id.date_order,
                'partner_id': line.order_id.partner_id.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'salesperson_id': line.order_id.user_id.id,
                'team_id': line.order_id.team_id.id,
                'state': line.order_id.state,
            }))
        self.sale_history_ids = vals


class ProductSaleHistoryLineContact(models.TransientModel):
    _inherit = 'product.sale.history.line'

    partner_id = fields.Many2one('res.partner', string='Client', readonly=True)
