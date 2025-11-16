# models/account_move.py, sale_order.py, purchase_order.py, stock_picking.py, etc.
 
# models/stock_picking.py
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    can_edit_location = fields.Boolean(
        string='Peut modifier les emplacements',
        compute='_compute_can_edit_location',
        store=True
    )

    @api.depends('state')
    def _compute_can_edit_location(self):
        for record in self:
            record.can_edit_location = False

    def action_enable_location_edit(self):
        self.ensure_one()
        if not self.env.user.has_group('adi_transfert_stock.group_location_edit'):
            raise UserError('Vous n\'avez pas les droits pour modifier les emplacements.')
        self.can_edit_location = True
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }