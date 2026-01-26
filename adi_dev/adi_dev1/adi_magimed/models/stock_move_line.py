# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Display fields for lot information
    lot_expiration_date = fields.Datetime(
        string='Date Expiration Lot',
        related='lot_id.expiration_date',
        readonly=True
    )
    lot_days_to_expiration = fields.Integer(
        string='Jours Avant Expiration',
        related='lot_id.days_to_expiration',
        readonly=True
    )
    lot_expiration_status = fields.Selection(
        related='lot_id.expiration_status',
        string='Statut Expiration',
        readonly=True
    )

    @api.onchange('lot_name')
    def _onchange_lot_name_auto_create(self):
        """Auto-create lot if configured on product"""
        if self.lot_name and self.product_id and self.product_id.auto_lot_on_receipt:
            # Check if lot already exists
            existing = self.env['stock.production.lot'].search([
                ('name', '=', self.lot_name),
                ('product_id', '=', self.product_id.id),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            if not existing and self.picking_id.picking_type_id.use_create_lots:
                # Will be created on validation
                pass

    def action_quick_create_lot(self):
        """Open wizard for quick lot creation"""
        self.ensure_one()
        return {
            'name': 'Creation Rapide de Lot',
            'type': 'ir.actions.act_window',
            'res_model': 'lot.quick.create.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_id': self.product_id.id,
                'default_move_line_id': self.id,
                'default_company_id': self.company_id.id,
            }
        }


class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_ids = fields.Many2many(
        'stock.production.lot',
        string='Lots',
        compute='_compute_lot_ids',
        help="Lots associes a ce mouvement"
    )
    lot_names_display = fields.Char(
        string='Numeros de Lot',
        compute='_compute_lot_names_display',
        help="Liste des numeros de lot"
    )

    def _compute_lot_ids(self):
        for move in self:
            move.lot_ids = move.move_line_ids.mapped('lot_id')

    def _compute_lot_names_display(self):
        for move in self:
            lots = move.move_line_ids.mapped('lot_id')
            move.lot_names_display = ', '.join(lots.mapped('name')) if lots else ''
