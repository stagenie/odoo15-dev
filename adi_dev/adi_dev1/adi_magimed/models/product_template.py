# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Fields for lot management
    expiration_alert_days = fields.Integer(
        string='Alerte Expiration (jours)',
        default=30,
        help="Nombre de jours avant expiration pour declencher l'alerte"
    )
    auto_lot_on_receipt = fields.Boolean(
        string='Generation Auto Lot',
        default=False,
        help="Generer automatiquement un numero de lot a la reception"
    )
    lot_prefix = fields.Char(
        string='Prefixe Lot',
        help="Prefixe pour la generation automatique des numeros de lot"
    )

    @api.onchange('tracking')
    def _onchange_tracking_lot(self):
        """Set default expiration alert when tracking is enabled"""
        if self.tracking in ('lot', 'serial'):
            if not self.expiration_alert_days:
                self.expiration_alert_days = 30


class ProductProduct(models.Model):
    _inherit = 'product.product'

    lot_count = fields.Integer(
        string='Nombre de Lots',
        compute='_compute_lot_count',
        help="Nombre de lots actifs pour ce produit"
    )
    expiring_lot_count = fields.Integer(
        string='Lots Expirant',
        compute='_compute_expiring_lot_count',
        help="Nombre de lots arrivant a expiration"
    )

    def _compute_lot_count(self):
        for product in self:
            product.lot_count = self.env['stock.production.lot'].search_count([
                ('product_id', '=', product.id),
                ('product_qty', '>', 0)
            ])

    def _compute_expiring_lot_count(self):
        today = fields.Date.today()
        for product in self:
            alert_days = product.expiration_alert_days or 30
            alert_date = fields.Date.add(today, days=alert_days)
            product.expiring_lot_count = self.env['stock.production.lot'].search_count([
                ('product_id', '=', product.id),
                ('product_qty', '>', 0),
                ('expiration_date', '!=', False),
                ('expiration_date', '<=', alert_date)
            ])

    def action_view_lots(self):
        """Open lots for this product"""
        self.ensure_one()
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        action['context'] = {'default_product_id': self.id}
        return action

    def action_view_expiring_lots(self):
        """Open expiring lots for this product"""
        self.ensure_one()
        today = fields.Date.today()
        alert_days = self.expiration_alert_days or 30
        alert_date = fields.Date.add(today, days=alert_days)
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [
            ('product_id', '=', self.id),
            ('product_qty', '>', 0),
            ('expiration_date', '!=', False),
            ('expiration_date', '<=', alert_date)
        ]
        action['context'] = {'default_product_id': self.id}
        return action
