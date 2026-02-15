from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    has_discount = fields.Boolean(
        string="Has Discount", compute="_compute_has_discount", store=True
    )

    @api.depends("invoice_line_ids.discount")
    def _compute_has_discount(self):
        for move in self:
            move.has_discount = any(line.discount > 0 for line in move.invoice_line_ids)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_unit_after_discount = fields.Float(
        string="Prix Unitaire Après Remise",
        compute="_compute_price_unit_after_discount",
        store=True
    )

    @api.depends('price_unit', 'discount')
    def _compute_price_unit_after_discount(self):
        for line in self:
            line.price_unit_after_discount = line.price_unit * (1 - (line.discount / 100))

    has_discount = fields.Boolean(
        string="Has Discount",
        compute="_compute_has_discount",
        store=True
    )

    @api.depends("move_id.has_discount")
    def _compute_has_discount(self):
        for line in self:
            line.has_discount = line.move_id.has_discount



