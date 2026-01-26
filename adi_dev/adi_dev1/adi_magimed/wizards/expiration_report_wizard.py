# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ExpirationReportWizard(models.TransientModel):
    _name = 'expiration.report.wizard'
    _description = 'Assistant Rapport Expiration'

    # Filters
    days_before_expiration = fields.Integer(
        string='Jours Avant Expiration',
        default=30,
        help="Afficher les lots expirant dans les X prochains jours"
    )
    include_expired = fields.Boolean(
        string='Inclure les Expires',
        default=False
    )
    product_ids = fields.Many2many(
        'product.product',
        string='Produits'
    )
    categ_ids = fields.Many2many(
        'product.category',
        string='Categories'
    )
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='Entrepots'
    )
    location_ids = fields.Many2many(
        'stock.location',
        string='Emplacements'
    )
    min_qty = fields.Float(
        string='Quantite Minimum',
        default=0,
        help="Afficher uniquement les lots avec au moins cette quantite"
    )

    @api.onchange('warehouse_ids')
    def _onchange_warehouse_ids(self):
        if self.warehouse_ids:
            return {
                'domain': {
                    'location_ids': [
                        ('usage', '=', 'internal'),
                        '|',
                        ('warehouse_id', 'in', self.warehouse_ids.ids),
                        ('id', 'in', self.warehouse_ids.mapped('lot_stock_id').ids)
                    ]
                }
            }
        return {'domain': {'location_ids': [('usage', '=', 'internal')]}}

    def _get_lots(self):
        """Get lots matching the filters"""
        today = fields.Date.today()
        alert_date = fields.Date.add(today, days=self.days_before_expiration)

        domain = [
            ('expiration_date', '!=', False),
            ('product_qty', '>=', self.min_qty)
        ]

        if self.include_expired:
            domain.append(('expiration_date', '<=', alert_date))
        else:
            domain.extend([
                ('expiration_date', '<=', alert_date),
                ('expiration_date', '>=', today)
            ])

        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))

        if self.categ_ids:
            domain.append(('product_id.categ_id', 'in', self.categ_ids.ids))

        lots = self.env['stock.production.lot'].search(domain, order='expiration_date asc')

        # Filter by location if specified
        if self.location_ids:
            filtered_lots = self.env['stock.production.lot']
            for lot in lots:
                quants = self.env['stock.quant'].search([
                    ('lot_id', '=', lot.id),
                    ('location_id', 'in', self.location_ids.ids),
                    ('quantity', '>', 0)
                ])
                if quants:
                    filtered_lots |= lot
            return filtered_lots

        # Filter by warehouse if specified
        if self.warehouse_ids:
            location_ids = self.warehouse_ids.mapped('lot_stock_id').ids
            filtered_lots = self.env['stock.production.lot']
            for lot in lots:
                quants = self.env['stock.quant'].search([
                    ('lot_id', '=', lot.id),
                    ('location_id', 'child_of', location_ids),
                    ('quantity', '>', 0)
                ])
                if quants:
                    filtered_lots |= lot
            return filtered_lots

        return lots

    def action_view_expiring_lots(self):
        """Open view with expiring lots"""
        self.ensure_one()
        lots = self._get_lots()

        return {
            'name': 'Lots Expirants',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.production.lot',
            'view_mode': 'tree,form,kanban',
            'view_ids': [
                (5, 0, 0),
                (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('adi_magimed.view_expiration_alert_tree').id}),
                (0, 0, {'view_mode': 'kanban', 'view_id': self.env.ref('adi_magimed.view_expiration_alert_kanban').id}),
            ],
            'domain': [('id', 'in', lots.ids)],
            'context': {}
        }

    def action_print_expiration_report(self):
        """Print expiration report"""
        self.ensure_one()
        lots = self._get_lots()

        return self.env.ref('adi_magimed.action_report_expiration_alert').report_action(
            lots,
            data={
                'days_before_expiration': self.days_before_expiration,
                'include_expired': self.include_expired,
                'filters': {
                    'products': self.product_ids.mapped('display_name'),
                    'categories': self.categ_ids.mapped('complete_name'),
                    'warehouses': self.warehouse_ids.mapped('name'),
                    'locations': self.location_ids.mapped('complete_name'),
                }
            }
        )
