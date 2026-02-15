# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    magimed_entry_type_id = fields.Many2one(
        'stock.picking.type', string="Bon d'Entree", check_company=True)
    magimed_exit_type_id = fields.Many2one(
        'stock.picking.type', string='Bon de Sortie', check_company=True)
    magimed_transfer_type_id = fields.Many2one(
        'stock.picking.type', string='Bon de Transfert', check_company=True)

    @api.model
    def create(self, vals):
        warehouse = super().create(vals)
        warehouse._create_magimed_picking_types()
        return warehouse

    def _create_magimed_picking_types(self):
        """Create MAGIMED picking types (Bon d'Entree, Sortie, Transfert) for this warehouse."""
        self.ensure_one()
        IrSequence = self.env['ir.sequence'].sudo()
        PickingType = self.env['stock.picking.type']

        # Get virtual locations
        production_loc = self.env.ref('adi_magimed.stock_location_production', raise_if_not_found=False)
        consumption_loc = self.env.ref('adi_magimed.stock_location_consumption', raise_if_not_found=False)

        # Get next color
        all_colors = [r['color'] for r in PickingType.search_read(
            [('warehouse_id', '!=', False), ('color', '!=', False)], ['color'], order='color')]
        available = [c for c in range(0, 12) if c not in all_colors]
        color = available[0] if available else 0

        # Get max sequence for ordering
        max_seq = PickingType.search_read(
            [('sequence', '!=', False)], ['sequence'], limit=1, order='sequence desc')
        max_seq = max_seq[0]['sequence'] if max_seq else 0

        wh_code = self.code

        # 1. Bon d'Entree
        entry_seq = IrSequence.create({
            'name': '%s Sequence Bon Entree' % self.name,
            'prefix': '%s/BE/%%(year)s/' % wh_code,
            'padding': 5,
            'company_id': self.company_id.id,
        })
        entry_type = PickingType.create({
            'name': "Bon d'Entree",
            'code': 'incoming',
            'sequence_code': 'BE',
            'use_create_lots': True,
            'use_existing_lots': False,
            'show_operations': True,
            'show_reserved': True,
            'default_location_src_id': production_loc.id if production_loc else False,
            'default_location_dest_id': self.lot_stock_id.id,
            'warehouse_id': self.id,
            'sequence_id': entry_seq.id,
            'sequence': max_seq + 10,
            'color': color,
            'company_id': self.company_id.id,
            'is_magimed_type': True,
            'magimed_operation': 'entry',
        })

        # 2. Bon de Sortie
        exit_seq = IrSequence.create({
            'name': '%s Sequence Bon Sortie' % self.name,
            'prefix': '%s/BS/%%(year)s/' % wh_code,
            'padding': 5,
            'company_id': self.company_id.id,
        })
        exit_type = PickingType.create({
            'name': 'Bon de Sortie',
            'code': 'outgoing',
            'sequence_code': 'BS',
            'use_create_lots': False,
            'use_existing_lots': True,
            'show_operations': True,
            'show_reserved': True,
            'default_location_src_id': self.lot_stock_id.id,
            'default_location_dest_id': consumption_loc.id if consumption_loc else False,
            'warehouse_id': self.id,
            'sequence_id': exit_seq.id,
            'sequence': max_seq + 11,
            'color': color,
            'company_id': self.company_id.id,
            'is_magimed_type': True,
            'magimed_operation': 'exit',
        })

        # 3. Bon de Transfert
        transfer_seq = IrSequence.create({
            'name': '%s Sequence Bon Transfert' % self.name,
            'prefix': '%s/BT/%%(year)s/' % wh_code,
            'padding': 5,
            'company_id': self.company_id.id,
        })
        transfer_type = PickingType.create({
            'name': 'Bon de Transfert',
            'code': 'internal',
            'sequence_code': 'BT',
            'use_create_lots': False,
            'use_existing_lots': True,
            'show_operations': True,
            'show_reserved': True,
            'default_location_src_id': self.lot_stock_id.id,
            'default_location_dest_id': self.lot_stock_id.id,
            'warehouse_id': self.id,
            'sequence_id': transfer_seq.id,
            'sequence': max_seq + 12,
            'color': color,
            'company_id': self.company_id.id,
            'is_magimed_type': True,
            'magimed_operation': 'transfer',
        })

        self.write({
            'magimed_entry_type_id': entry_type.id,
            'magimed_exit_type_id': exit_type.id,
            'magimed_transfer_type_id': transfer_type.id,
        })
