# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMoveHistoryWizard(models.TransientModel):
    _name = 'stock.move.history.wizard'
    _description = 'Assistant Historique des Mouvements'

    # Filters
    date_from = fields.Date(
        string='Date Debut',
        default=lambda self: fields.Date.add(fields.Date.today(), months=-1)
    )
    date_to = fields.Date(
        string='Date Fin',
        default=fields.Date.today
    )
    product_ids = fields.Many2many(
        'product.product',
        string='Produits'
    )
    lot_ids = fields.Many2many(
        'stock.production.lot',
        string='Lots'
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
        'stock_history_wizard_location_rel',
        'wizard_id', 'location_id',
        string='Emplacements'
    )
    move_type = fields.Selection([
        ('all', 'Tous'),
        ('in', 'Entrees'),
        ('out', 'Sorties'),
        ('internal', 'Transferts')
    ], string='Type de Mouvement', default='all')
    with_lot_only = fields.Boolean(
        string='Uniquement avec Lot',
        default=False
    )

    @api.onchange('warehouse_ids')
    def _onchange_warehouse_ids(self):
        """Filter locations based on selected warehouses"""
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

    def _build_domain(self):
        """Build search domain from wizard filters"""
        domain = []

        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', fields.Datetime.end_of(
                fields.Datetime.to_datetime(self.date_to), 'day')))

        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))

        if self.lot_ids:
            domain.append(('lot_id', 'in', self.lot_ids.ids))

        if self.categ_ids:
            domain.append(('categ_id', 'in', self.categ_ids.ids))

        if self.warehouse_ids:
            domain.append(('warehouse_id', 'in', self.warehouse_ids.ids))

        if self.location_ids:
            domain.append('|')
            domain.append(('location_id', 'in', self.location_ids.ids))
            domain.append(('location_dest_id', 'in', self.location_ids.ids))

        if self.move_type and self.move_type != 'all':
            domain.append(('move_type', '=', self.move_type))

        if self.with_lot_only:
            domain.append(('lot_id', '!=', False))

        return domain

    def action_view_history(self):
        """Open history view with applied filters"""
        self.ensure_one()
        domain = self._build_domain()

        return {
            'name': 'Historique des Mouvements',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move.history',
            'view_mode': 'tree,pivot,graph',
            'domain': domain,
            'context': {
                'search_default_group_by_date': 1,
            }
        }

    def action_print_history(self):
        """Print history report"""
        self.ensure_one()
        domain = self._build_domain()

        # Get records
        history = self.env['stock.move.history'].search(domain, order='date desc')

        return self.env.ref('adi_magimed.action_report_stock_history').report_action(
            history,
            data={
                'date_from': self.date_from,
                'date_to': self.date_to,
                'filters': {
                    'products': self.product_ids.mapped('display_name'),
                    'lots': self.lot_ids.mapped('name'),
                    'warehouses': self.warehouse_ids.mapped('name'),
                    'locations': self.location_ids.mapped('complete_name'),
                    'move_type': dict(self._fields['move_type'].selection).get(self.move_type),
                }
            }
        )
