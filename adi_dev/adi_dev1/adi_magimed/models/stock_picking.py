# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Additional fields for enhanced transfer report
    is_magimed_entry = fields.Boolean(
        string='Bon d\'Entree MAGIMED',
        compute='_compute_magimed_type',
        store=True
    )
    is_magimed_exit = fields.Boolean(
        string='Bon de Sortie MAGIMED',
        compute='_compute_magimed_type',
        store=True
    )
    is_magimed_transfer = fields.Boolean(
        string='Bon de Transfert MAGIMED',
        compute='_compute_magimed_type',
        store=True
    )

    source_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Entrepot Source',
        compute='_compute_warehouses',
        store=True
    )
    dest_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Entrepot Destination',
        compute='_compute_warehouses',
        store=True
    )

    lot_info = fields.Text(
        string='Info Lots',
        compute='_compute_lot_info',
        help="Resume des lots transferes"
    )
    has_lots = fields.Boolean(
        string='Contient des Lots',
        compute='_compute_has_lots'
    )

    entry_reason = fields.Selection([
        ('production', 'Production'),
        ('return', 'Retour'),
        ('adjustment', 'Ajustement'),
        ('other', 'Autre')
    ], string='Motif Entree', default='production')

    exit_reason = fields.Selection([
        ('consumption', 'Consommation'),
        ('scrap', 'Rebut'),
        ('adjustment', 'Ajustement'),
        ('other', 'Autre')
    ], string='Motif Sortie', default='consumption')

    transfer_notes = fields.Text(
        string='Notes de Transfert',
        help="Notes additionnelles pour le transfert"
    )

    @api.depends('picking_type_id')
    def _compute_magimed_type(self):
        entry_type = self.env.ref('adi_magimed.picking_type_stock_entry', raise_if_not_found=False)
        exit_type = self.env.ref('adi_magimed.picking_type_stock_exit', raise_if_not_found=False)
        transfer_type = self.env.ref('adi_magimed.picking_type_stock_transfer', raise_if_not_found=False)

        for picking in self:
            picking.is_magimed_entry = entry_type and picking.picking_type_id.id == entry_type.id
            picking.is_magimed_exit = exit_type and picking.picking_type_id.id == exit_type.id
            picking.is_magimed_transfer = transfer_type and picking.picking_type_id.id == transfer_type.id

    @api.depends('location_id', 'location_dest_id')
    def _compute_warehouses(self):
        for picking in self:
            # Find source warehouse
            source_wh = self.env['stock.warehouse'].search([
                ('lot_stock_id', 'parent_of', picking.location_id.id)
            ], limit=1)
            if not source_wh:
                source_wh = self.env['stock.warehouse'].search([
                    ('view_location_id', 'parent_of', picking.location_id.id)
                ], limit=1)
            picking.source_warehouse_id = source_wh.id if source_wh else False

            # Find destination warehouse
            dest_wh = self.env['stock.warehouse'].search([
                ('lot_stock_id', 'parent_of', picking.location_dest_id.id)
            ], limit=1)
            if not dest_wh:
                dest_wh = self.env['stock.warehouse'].search([
                    ('view_location_id', 'parent_of', picking.location_dest_id.id)
                ], limit=1)
            picking.dest_warehouse_id = dest_wh.id if dest_wh else False

    def _compute_lot_info(self):
        for picking in self:
            lot_lines = []
            for move_line in picking.move_line_ids_without_package:
                if move_line.lot_id:
                    expiry = move_line.lot_id.expiration_date
                    expiry_str = expiry.strftime('%d/%m/%Y') if expiry else 'N/A'
                    lot_lines.append(
                        f"{move_line.product_id.display_name}: "
                        f"Lot {move_line.lot_id.name} (Exp: {expiry_str}) - "
                        f"Qte: {move_line.qty_done}"
                    )
            picking.lot_info = '\n'.join(lot_lines) if lot_lines else ''

    def _compute_has_lots(self):
        for picking in self:
            picking.has_lots = any(
                line.lot_id for line in picking.move_line_ids_without_package
            )

    def action_print_bon_entree(self):
        """Print Bon d'Entree report"""
        return self.env.ref('adi_magimed.action_report_bon_entree').report_action(self)

    def action_print_bon_sortie(self):
        """Print Bon de Sortie report"""
        return self.env.ref('adi_magimed.action_report_bon_sortie').report_action(self)

    def action_print_bon_transfert(self):
        """Print Bon de Transfert report"""
        return self.env.ref('adi_magimed.action_report_bon_transfert').report_action(self)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_magimed_type = fields.Boolean(
        string='Type MAGIMED',
        default=False,
        help="Indique si c'est un type d'operation MAGIMED"
    )
    magimed_operation = fields.Selection([
        ('entry', 'Bon d\'Entree'),
        ('exit', 'Bon de Sortie'),
        ('transfer', 'Bon de Transfert')
    ], string='Operation MAGIMED')
