# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class StockMoveHistory(models.Model):
    _name = 'stock.move.history'
    _description = 'Historique des Mouvements de Stock'
    _auto = False
    _order = 'date desc'

    # Basic fields
    date = fields.Datetime(string='Date', readonly=True)
    reference = fields.Char(string='Reference', readonly=True)
    origin = fields.Char(string='Origine', readonly=True)

    # Product info
    product_id = fields.Many2one('product.product', string='Produit', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Modele Produit', readonly=True)
    categ_id = fields.Many2one('product.category', string='Categorie', readonly=True)

    # Quantity
    qty_done = fields.Float(string='Quantite', readonly=True, digits='Product Unit of Measure')
    product_uom_id = fields.Many2one('uom.uom', string='Unite', readonly=True)

    # Lot info
    lot_id = fields.Many2one('stock.production.lot', string='Lot', readonly=True)
    lot_name = fields.Char(string='Numero Lot', readonly=True)
    expiration_date = fields.Datetime(string='Date Expiration', readonly=True)

    # Location info
    location_id = fields.Many2one('stock.location', string='Emplacement Source', readonly=True)
    location_dest_id = fields.Many2one('stock.location', string='Emplacement Destination', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Entrepot', readonly=True)

    # Picking info
    picking_id = fields.Many2one('stock.picking', string='Transfert', readonly=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Type Operation', readonly=True)

    # Operation type
    move_type = fields.Selection([
        ('in', 'Entree'),
        ('out', 'Sortie'),
        ('internal', 'Transfert')
    ], string='Type Mouvement', readonly=True)

    # Partner info
    partner_id = fields.Many2one('res.partner', string='Partenaire', readonly=True)

    # User info
    user_id = fields.Many2one('res.users', string='Utilisateur', readonly=True)
    company_id = fields.Many2one('res.company', string='Societe', readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting', 'En Attente'),
        ('confirmed', 'Confirme'),
        ('assigned', 'Disponible'),
        ('done', 'Fait'),
        ('cancel', 'Annule')
    ], string='Etat', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    sml.id as id,
                    sml.date as date,
                    sm.reference as reference,
                    sm.origin as origin,
                    sml.product_id as product_id,
                    pp.product_tmpl_id as product_tmpl_id,
                    pt.categ_id as categ_id,
                    sml.qty_done as qty_done,
                    sml.product_uom_id as product_uom_id,
                    sml.lot_id as lot_id,
                    spl.name as lot_name,
                    spl.expiration_date as expiration_date,
                    sml.location_id as location_id,
                    sml.location_dest_id as location_dest_id,
                    COALESCE(sw_src.id, sw_dest.id) as warehouse_id,
                    sm.picking_id as picking_id,
                    sp.picking_type_id as picking_type_id,
                    CASE
                        WHEN sl_src.usage = 'internal' AND sl_dest.usage = 'internal' THEN 'internal'
                        WHEN sl_dest.usage = 'internal' THEN 'in'
                        WHEN sl_src.usage = 'internal' THEN 'out'
                        ELSE 'internal'
                    END as move_type,
                    COALESCE(sm.partner_id, sp.partner_id) as partner_id,
                    sm.write_uid as user_id,
                    sml.company_id as company_id,
                    sm.state as state
                FROM stock_move_line sml
                JOIN stock_move sm ON sm.id = sml.move_id
                JOIN product_product pp ON pp.id = sml.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN stock_production_lot spl ON spl.id = sml.lot_id
                LEFT JOIN stock_location sl_src ON sl_src.id = sml.location_id
                LEFT JOIN stock_location sl_dest ON sl_dest.id = sml.location_dest_id
                LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
                LEFT JOIN stock_warehouse sw_src ON sw_src.lot_stock_id = sl_src.id
                LEFT JOIN stock_warehouse sw_dest ON sw_dest.lot_stock_id = sl_dest.id
                WHERE sm.state = 'done'
                AND sml.qty_done > 0
            )
        """ % self._table)

    def action_view_picking(self):
        """Open related picking"""
        self.ensure_one()
        if self.picking_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'res_id': self.picking_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return True

    def action_view_lot(self):
        """Open related lot"""
        self.ensure_one()
        if self.lot_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.production.lot',
                'res_id': self.lot_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return True
