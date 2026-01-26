# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import timedelta


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    # Computed fields for expiration management
    alert_date = fields.Date(
        string='Date Alerte',
        compute='_compute_alert_date',
        store=True,
        help="Date a partir de laquelle l'alerte d'expiration est declenchee"
    )
    is_expired = fields.Boolean(
        string='Expire',
        compute='_compute_expiration_status',
        search='_search_is_expired',
        help="Indique si le lot est expire"
    )
    is_expiring_soon = fields.Boolean(
        string='Expire Bientot',
        compute='_compute_expiration_status',
        search='_search_is_expiring_soon',
        help="Indique si le lot arrive a expiration"
    )
    days_to_expiration = fields.Integer(
        string='Jours Avant Expiration',
        compute='_compute_days_to_expiration',
        help="Nombre de jours restants avant expiration"
    )
    expiration_status = fields.Selection([
        ('ok', 'OK'),
        ('warning', 'Attention'),
        ('danger', 'Urgent'),
        ('expired', 'Expire')
    ], string='Statut Expiration', compute='_compute_expiration_status')

    total_qty = fields.Float(
        string='Quantite Totale',
        compute='_compute_total_qty',
        digits='Product Unit of Measure',
        help="Quantite totale en stock pour ce lot"
    )
    location_ids = fields.Many2many(
        'stock.location',
        string='Emplacements',
        compute='_compute_locations',
        help="Emplacements contenant ce lot"
    )
    location_qty_info = fields.Text(
        string='Detail par Emplacement',
        compute='_compute_location_qty_info',
        help="Quantites par emplacement"
    )

    @api.depends('expiration_date', 'product_id.expiration_alert_days')
    def _compute_alert_date(self):
        for lot in self:
            if lot.expiration_date:
                alert_days = lot.product_id.expiration_alert_days or 30
                lot.alert_date = lot.expiration_date - timedelta(days=alert_days)
            else:
                lot.alert_date = False

    @api.depends('expiration_date', 'alert_date')
    def _compute_expiration_status(self):
        today = fields.Date.today()
        for lot in self:
            if not lot.expiration_date:
                lot.is_expired = False
                lot.is_expiring_soon = False
                lot.expiration_status = 'ok'
            elif lot.expiration_date < today:
                lot.is_expired = True
                lot.is_expiring_soon = False
                lot.expiration_status = 'expired'
            elif lot.alert_date and lot.alert_date <= today:
                lot.is_expired = False
                lot.is_expiring_soon = True
                # Determine urgency level
                days_left = (lot.expiration_date - today).days
                if days_left <= 7:
                    lot.expiration_status = 'danger'
                else:
                    lot.expiration_status = 'warning'
            else:
                lot.is_expired = False
                lot.is_expiring_soon = False
                lot.expiration_status = 'ok'

    def _search_is_expired(self, operator, value):
        today = fields.Date.today()
        if operator == '=' and value:
            return [('expiration_date', '<', today)]
        elif operator == '=' and not value:
            return ['|', ('expiration_date', '>=', today), ('expiration_date', '=', False)]
        return []

    def _search_is_expiring_soon(self, operator, value):
        today = fields.Date.today()
        if operator == '=' and value:
            return [
                ('expiration_date', '>=', today),
                ('alert_date', '<=', today)
            ]
        return []

    @api.depends('expiration_date')
    def _compute_days_to_expiration(self):
        today = fields.Date.today()
        for lot in self:
            if lot.expiration_date:
                delta = lot.expiration_date - today
                lot.days_to_expiration = delta.days
            else:
                lot.days_to_expiration = 9999

    def _compute_total_qty(self):
        for lot in self:
            quants = self.env['stock.quant'].search([
                ('lot_id', '=', lot.id),
                ('location_id.usage', '=', 'internal')
            ])
            lot.total_qty = sum(quants.mapped('quantity'))

    def _compute_locations(self):
        for lot in self:
            quants = self.env['stock.quant'].search([
                ('lot_id', '=', lot.id),
                ('location_id.usage', '=', 'internal'),
                ('quantity', '>', 0)
            ])
            lot.location_ids = quants.mapped('location_id')

    def _compute_location_qty_info(self):
        for lot in self:
            quants = self.env['stock.quant'].search([
                ('lot_id', '=', lot.id),
                ('location_id.usage', '=', 'internal'),
                ('quantity', '>', 0)
            ])
            info_lines = []
            for quant in quants:
                info_lines.append(f"{quant.location_id.complete_name}: {quant.quantity} {lot.product_uom_id.name}")
            lot.location_qty_info = '\n'.join(info_lines) if info_lines else 'Aucun stock'

    @api.model
    def generate_lot_name(self, product=None):
        """Generate a unique lot name using sequence"""
        prefix = ''
        if product and product.lot_prefix:
            prefix = product.lot_prefix
        sequence = self.env['ir.sequence'].next_by_code('stock.production.lot.magimed')
        return f"{prefix}{sequence}" if prefix else sequence

    @api.model
    def get_expiring_lots(self, days=30, product_ids=None, location_ids=None):
        """Get lots expiring within specified days"""
        today = fields.Date.today()
        alert_date = fields.Date.add(today, days=days)

        domain = [
            ('expiration_date', '!=', False),
            ('expiration_date', '<=', alert_date),
            ('expiration_date', '>=', today),
            ('product_qty', '>', 0)
        ]

        if product_ids:
            domain.append(('product_id', 'in', product_ids))

        lots = self.search(domain, order='expiration_date asc')

        if location_ids:
            # Filter by location
            filtered_lots = self.env['stock.production.lot']
            for lot in lots:
                quants = self.env['stock.quant'].search([
                    ('lot_id', '=', lot.id),
                    ('location_id', 'in', location_ids),
                    ('quantity', '>', 0)
                ])
                if quants:
                    filtered_lots |= lot
            return filtered_lots

        return lots

    def action_send_expiration_alert(self):
        """Send expiration alert email"""
        template = self.env.ref('adi_magimed.mail_template_expiration_alert', raise_if_not_found=False)
        if template:
            for lot in self:
                template.send_mail(lot.id, force_send=True)
        return True
