# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta, datetime
import logging

_logger = logging.getLogger(__name__)


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    # Note: alert_date is already defined by product_expiry as Datetime - do not redefine it
    # Computed fields for expiration management
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
        store=True,
        help="Nombre de jours restants avant expiration"
    )
    expiration_status = fields.Selection([
        ('ok', 'OK'),
        ('warning', 'Attention'),
        ('danger', 'Urgent'),
        ('expired', 'Expire')
    ], string='Statut Expiration', compute='_compute_expiration_status', store=True)

    lot_alert_days = fields.Integer(
        string="Jours Avant Alerte",
        compute='_compute_lot_alert_days',
        inverse='_inverse_lot_alert_days',
        help="Nombre de jours avant la date de peremption pour declencher l'alerte. "
             "Modifier ce champ recalcule automatiquement la date d'alerte."
    )

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

    @api.depends('expiration_date', 'alert_date')
    def _compute_expiration_status(self):
        now = fields.Datetime.now()
        for lot in self:
            if not lot.expiration_date:
                lot.is_expired = False
                lot.is_expiring_soon = False
                lot.expiration_status = 'ok'
            elif lot.expiration_date < now:
                lot.is_expired = True
                lot.is_expiring_soon = False
                lot.expiration_status = 'expired'
            elif lot.alert_date and lot.alert_date <= now:
                lot.is_expired = False
                lot.is_expiring_soon = True
                # Determine urgency level
                days_left = (lot.expiration_date - now).days
                if days_left <= 7:
                    lot.expiration_status = 'danger'
                else:
                    lot.expiration_status = 'warning'
            else:
                lot.is_expired = False
                lot.is_expiring_soon = False
                lot.expiration_status = 'ok'

    def _search_is_expired(self, operator, value):
        now = fields.Datetime.now()
        if operator == '=' and value:
            return [('expiration_date', '<', now)]
        elif operator == '=' and not value:
            return ['|', ('expiration_date', '>=', now), ('expiration_date', '=', False)]
        return []

    def _search_is_expiring_soon(self, operator, value):
        now = fields.Datetime.now()
        if operator == '=' and value:
            return [
                ('expiration_date', '>=', now),
                ('alert_date', '<=', now)
            ]
        return []

    @api.depends('expiration_date', 'alert_date')
    def _compute_lot_alert_days(self):
        for lot in self:
            if lot.expiration_date and lot.alert_date:
                lot.lot_alert_days = (lot.expiration_date - lot.alert_date).days
            elif lot.expiration_date:
                # Default from product template
                lot.lot_alert_days = lot.product_id.alert_time or 30
            else:
                lot.lot_alert_days = 0

    def _inverse_lot_alert_days(self):
        for lot in self:
            if lot.expiration_date and lot.lot_alert_days >= 0:
                lot.alert_date = lot.expiration_date - timedelta(days=lot.lot_alert_days)

    @api.onchange('lot_alert_days')
    def _onchange_lot_alert_days(self):
        """Recalculate alert_date when lot_alert_days changes"""
        if self.expiration_date and self.lot_alert_days >= 0:
            self.alert_date = self.expiration_date - timedelta(days=self.lot_alert_days)

    def _get_default_alert_days(self):
        """Get default alert days from config parameter"""
        try:
            return int(self.env['ir.config_parameter'].sudo().get_param(
                'adi_magimed.default_expiration_alert_days', '30'))
        except (ValueError, TypeError):
            return 30

    @api.model_create_multi
    def create(self, vals_list):
        lots = super().create(vals_list)
        default_days = self._get_default_alert_days()
        for lot in lots:
            if lot.expiration_date and lot.alert_date:
                # If alert_date equals expiration_date (meaning alert_time=0 on product)
                if abs((lot.alert_date - lot.expiration_date).total_seconds()) < 60:
                    lot.alert_date = lot.expiration_date - timedelta(days=default_days)
        return lots

    @api.onchange('expiration_date')
    def _onchange_expiration_date_default_alert(self):
        """After product_expiry computes alert_date, ensure lot_alert_days >= default"""
        if self.expiration_date and self.alert_date:
            current_days = (self.expiration_date - self.alert_date).days
            if current_days <= 0:
                default_days = self._get_default_alert_days()
                self.alert_date = self.expiration_date - timedelta(days=default_days)

    @api.depends('expiration_date')
    def _compute_days_to_expiration(self):
        now = fields.Datetime.now()
        for lot in self:
            if lot.expiration_date:
                delta = lot.expiration_date - now
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
        today = fields.Datetime.now()
        alert_date = today + timedelta(days=days)

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
