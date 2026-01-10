# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    sh_pol_picking_order_line_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        related="picking_id.picking_type_id",
        ondelete='set null',
        store=True,
        string="Picking Type",
    )

    sh_pol_picking_order_line_picking_type_code = fields.Selection(
        related="picking_id.picking_type_id.code",
        store=True,
        string="Picking Operation",
    )


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sh_pol_picking_order_line_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        related="picking_id.picking_type_id",
        ondelete='set null',
        store=True,
        string="Picking Type",
    )

    sh_pol_picking_order_line_picking_type_code = fields.Selection(
        related="picking_id.picking_type_id.code",
        store=True,
        string="Picking Operation",
    )
    sh_pol_picking_order_line_origin = fields.Char(
        related="picking_id.origin",
        store=True,
    )
